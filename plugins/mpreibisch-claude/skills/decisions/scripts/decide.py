#!/usr/bin/env python3
"""Classify supplied text with fixed questions, or fail open to an LLM step."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import shlex
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


MODEL = "gpt-6-luna"
RUN = 10
TIMEOUT = 5.0
INPUT_LIMIT = 10_485_760


class DecisionError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Argument values can contain credentials or private text.
        raise DecisionError("invalid arguments; use --help for syntax")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def require(condition, reason):
    if not condition:
        raise DecisionError(reason)


def identity(value):
    return json.dumps(value, sort_keys=True)


def probability(value):
    require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1,
            "invalid probability in response")
    return value


def load_preset(name):
    require(re.fullmatch(r"[a-z][a-z0-9-]*", name) is not None, "invalid preset name")
    path = Path(__file__).resolve().parent.parent / "presets" / (name + ".json")
    preset = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(preset, dict) and type(preset.get("calibrated")) is bool, "invalid preset calibration")
    require(isinstance(preset.get("input_template"), str) and preset["input_template"].strip(),
            "preset needs an input template")
    require("questions" in preset and "gate" in preset, "preset needs questions and a gate")
    return preset


def load_questions(args, preset=None):
    if preset:
        require(not (args.questions or args.predicate or args.choice), "preset questions cannot be overridden")
        questions = preset["questions"]
    else:
        questions = json.loads(Path(args.questions).read_text(encoding="utf-8")) if args.questions else []
    require(isinstance(questions, list), "questions must be a JSON array")
    for name, instructions in args.predicate:
        questions.append({"type": "predicate", "name": name, "instructions": instructions})
    for name, instructions, choices in args.choice:
        questions.append({"type": "choice", "name": name, "instructions": instructions,
                          "choices": json.loads(choices)})
    require(1 <= len(questions) <= 400, "provide between 1 and 400 questions")
    names = set()
    for index, question in enumerate(questions, 1):
        require(isinstance(question, dict), "invalid question")
        question.setdefault("name", f"question_{index}")
        name = question["name"]
        require(isinstance(name, str) and name.strip() and name not in names,
                "question names must be nonempty and unique")
        names.add(name)
        kind = question.get("type")
        require(kind in ("predicate", "choice", "score"), "invalid question type")
        require(isinstance(question.get("instructions"), str) and question["instructions"].strip(),
                "each question needs instructions")
        field = {"choice": "choices", "score": "levels"}.get(kind)
        require(set(question) <= {"type", "name", "instructions", field}, "unknown question field")
        if field:
            options = question.get(field)
            limit = 255 if kind == "choice" else 10
            require(isinstance(options, list) and 2 <= len(options) <= limit, "invalid option count")
            values = []
            for option in options:
                key = "value" if kind == "choice" else "label"
                require(isinstance(option, dict) and key in option, "invalid option")
                require(set(option) <= {key, "description"}, "unknown option field")
                require(type(option[key]) in ((str, bool) if kind == "choice" else (str,)),
                        "invalid option value")
                require("description" not in option or isinstance(option["description"], str),
                        "invalid option description")
                values.append(identity(option[key]))
            require(len(set(values)) == len(values), "option values must be unique")
    return questions


def parse_gates(expressions, questions):
    by_name = {question["name"]: question for question in questions}
    gates = []
    for expression in expressions:
        match = re.fullmatch(r"([^=<>]+)(?:=([^<>]+))?(>=|<=|>|<)([0-9.]+)", expression)
        require(match is not None, "invalid gate condition")
        name, value, operator, threshold = match.groups()
        try:
            threshold = float(threshold)
        except ValueError:
            raise DecisionError("invalid gate threshold") from None
        require(math.isfinite(threshold) and 0 <= threshold <= 1, "invalid gate threshold")
        question = by_name.get(name)
        require(question is not None, "gate names an unknown question")
        if question["type"] == "predicate":
            require(value is None, "predicate gates compare the true probability directly")
        else:
            field, key = ("choices", "value") if question["type"] == "choice" else ("levels", "label")
            candidates = [option[key] for option in question[field]
                          if (str(option[key]).lower() if type(option[key]) is bool else option[key]) == value]
            require(len(candidates) == 1, "gate option is missing, unknown, or ambiguous")
            value = candidates[0]
        gates.append((name, value, operator, threshold))
    return gates


def get_key(deadline):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        command = os.environ.get("DECISIONS_KEY_CMD", "")
        require(command.strip(), "set OPENAI_API_KEY or DECISIONS_KEY_CMD")
        try:
            result = subprocess.run(shlex.split(command), stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    timeout=max(0.01, deadline - time.monotonic()), check=True)
            key = result.stdout.decode("utf-8").strip()
        except Exception:
            raise DecisionError("key command failed") from None
    require(key and not any(character.isspace() for character in key), "invalid API key configuration")
    return key


def endpoint():
    base = os.environ.get("DECISIONS_BASE_URL")
    if base is None:
        return "https://api.openai.com/v1/decisions"
    parsed = urllib.parse.urlsplit(base)
    require(parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost", "::1")
            and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment,
            "DECISIONS_BASE_URL is only for a local test server")
    return base.rstrip("/") + "/decisions"


def request(body, key, url, deadline):
    # A daemon thread bounds the whole exchange, including a server that trickles bytes.
    output = queue.Queue()

    def send():
        try:
            handlers = [NoRedirect()]
            if os.environ.get("DECISIONS_BASE_URL") is not None:
                handlers.append(urllib.request.ProxyHandler({}))
            opener = urllib.request.build_opener(*handlers)
            for attempt in range(3):
                remaining = deadline - time.monotonic()
                require(remaining > 0, "request timed out")
                req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                             headers={"Authorization": "Bearer " + key,
                                                      "Content-Type": "application/json"})
                try:
                    with opener.open(req, timeout=remaining) as response:
                        raw = response.read(8_388_609)
                        require(len(raw) <= 8_388_608, "response is too large")
                        output.put(json.loads(raw))
                        return
                except urllib.error.HTTPError as error:
                    code = error.code
                    error.close()
                    if attempt == 2 or not (code == 429 or 500 <= code <= 599):
                        raise DecisionError(f"HTTP {code}") from None
                    time.sleep(min(0.2 * 2 ** attempt, max(0, deadline - time.monotonic())))
        except Exception as error:
            output.put(error)

    threading.Thread(target=send, daemon=True).start()
    try:
        result = output.get(timeout=max(0.01, deadline - time.monotonic()))
    except queue.Empty:
        raise DecisionError("request timed out") from None
    if isinstance(result, DecisionError):
        raise result
    if isinstance(result, Exception):
        raise DecisionError("request failed or response is not JSON")
    return result


def normalize(response, questions):
    require(isinstance(response, dict) and isinstance(response.get("model"), str)
            and response["model"].startswith(MODEL), "invalid response model")
    answers = response.get("answers")
    require(isinstance(answers, list) and len(answers) == len(questions), "invalid answer count")
    usage = response.get("usage")
    require(isinstance(usage, dict), "missing usage")
    for field in ("input_tokens", "output_tokens", "total_tokens"):
        require(type(usage.get(field)) is int and usage[field] >= 0, "invalid token usage")
    normalized = []
    for question, answer in zip(questions, answers):
        require(isinstance(answer, dict), "invalid answer")
        require(answer.get("type") != "refusal", "API refused a question")
        kind = question["type"]
        require(answer.get("type") == kind and answer.get("name") == question["name"],
                "answer type or name does not match the question")
        if kind == "predicate":
            p = probability(answer.get("probability"))
            chosen = p >= 0.5
            probabilities = [{"value": True, "probability": p}, {"value": False, "probability": 1 - p}]
        else:
            probability(answer.get("confidence"))
            probabilities = answer.get("probabilities")
            field, key = ("choices", "value") if kind == "choice" else ("levels", "label")
            expected = {identity(option[key]) for option in question[field]}
            require(isinstance(probabilities, list) and len(probabilities) == len(expected),
                    "invalid option probabilities")
            found = []
            for option in probabilities:
                require(isinstance(option, dict) and key in option, "invalid probability option")
                found.append(identity(option[key]))
                probability(option.get("probability"))
                if kind == "score":
                    require(type(option.get("value")) in (int, float) and math.isfinite(option["value"]),
                            "invalid score level value")
            require(set(found) == expected and len(set(found)) == len(found), "response options do not match")
            require(math.isclose(sum(option["probability"] for option in probabilities), 1, abs_tol=0.01),
                    "option probabilities do not sum to one")
            chosen = answer.get("choice" if kind == "choice" else "score")
            if kind == "choice":
                require(identity(chosen) in expected, "unknown chosen value")
                selected = next(option["probability"] for option in probabilities if identity(option["value"]) == identity(chosen))
                require(selected >= max(option["probability"] for option in probabilities), "inconsistent chosen value")
                probabilities = [{"value": option["value"], "probability": option["probability"]}
                                 for option in probabilities]
            else:
                require(type(chosen) in (int, float) and math.isfinite(chosen), "invalid score")
                probabilities = [{"label": option["label"], "value": option["value"],
                                  "probability": option["probability"]} for option in probabilities]
        normalized.append({"name": question["name"], "type": kind, "value": chosen, "probabilities": probabilities})
    return {"model": MODEL, "answers": normalized, "usage": usage}


def should_skip(gates, answers):
    passed = []
    by_name = {answer["name"]: answer for answer in answers}
    for name, value, operator, threshold in gates:
        answer = by_name[name]
        key = "label" if answer["type"] == "score" else "value"
        target = True if answer["type"] == "predicate" else value
        p = next(option["probability"] for option in answer["probabilities"]
                 if identity(option[key]) == identity(target))
        passed.append({">=": p >= threshold, "<=": p <= threshold, ">": p > threshold, "<": p < threshold}[operator])
    return bool(passed) and all(passed)


def parse_rule(rule, questions):
    require(isinstance(rule, dict) and set(rule) <= {"all", "any", "unless"}, "invalid gate rule")
    require(rule.get("all") or rule.get("any"), "gate rule needs conditions")
    parsed = {}
    for group in ("all", "any", "unless"):
        conditions = rule.get(group, [])
        require(isinstance(conditions, list) and all(isinstance(item, str) for item in conditions),
                "invalid gate conditions")
        parsed[group] = parse_gates(conditions, questions)
    return parsed


def rule_passes(rule, answers):
    return ((not rule["all"] or should_skip(rule["all"], answers))
            and (not rule["any"] or any(should_skip([condition], answers) for condition in rule["any"]))
            and not any(should_skip([condition], answers) for condition in rule["unless"]))


def encode(value, key):
    def redact(item):
        if isinstance(item, str):
            return item.replace(key, "[REDACTED]") if key else item
        if isinstance(item, dict):
            return {redact(name): redact(content) for name, content in item.items()}
        if isinstance(item, list):
            return [redact(content) for content in item]
        return item
    return json.dumps(redact(value), separators=(",", ":"), allow_nan=False)


def write_log(path, record, key):
    if path:
        try:
            with os.fdopen(os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600), "a", encoding="utf-8") as log:
                log.write(encode(record, key) + "\n")
        except Exception:
            raise DecisionError("cannot append decision log") from None


def main():
    parser = Parser(description=__doc__)
    parser.add_argument("--input", metavar="FILE", help="Read UTF-8 text from a file instead of stdin")
    parser.add_argument("--questions", metavar="FILE", help="Read a JSON array of API questions")
    parser.add_argument("--preset", metavar="NAME", help="Load bundled questions and a gate rule")
    parser.add_argument("--predicate", nargs=2, action="append", default=[], metavar=("NAME", "INSTRUCTIONS"))
    parser.add_argument("--choice", nargs=3, action="append", default=[], metavar=("NAME", "INSTRUCTIONS", "CHOICES_JSON"))
    parser.add_argument("--gate", nargs="?", const="", action="append", metavar="CONDITION",
                        help="Use preset rules, or require every explicit condition")
    parser.add_argument("--enforce", action="store_true", help="Enforce an uncalibrated preset gate instead of shadowing it")
    parser.add_argument("--log", metavar="FILE", help="Append answers and input metadata as JSONL")
    parser.add_argument("--check", action="store_true", help="Check configuration without a network call or stdin read")
    args = None
    key = ""
    started = time.monotonic()
    record = {"input_length": None, "input_sha256": None, "answers": [], "gate": "RUN"}
    try:
        args = parser.parse_args()
        gating = args.gate is not None
        require(not (args.check and gating), "--check cannot run a gate")
        require(not args.enforce or (args.preset and gating), "--enforce requires --preset and --gate")
        preset = load_preset(args.preset) if args.preset else None
        questions = load_questions(args, preset) if (not args.check or preset or args.questions or args.predicate or args.choice) else []
        preset_rule = parse_rule(preset["gate"], questions) if preset else None
        rule = None
        if gating:
            conditions = [condition for condition in args.gate if condition]
            require(conditions or preset, "bare --gate requires a preset")
            if conditions:
                rule = parse_rule({"all": conditions,
                                   "unless": preset["gate"].get("unless", []) if preset else []}, questions)
            else:
                rule = preset_rule
        shadow = bool(gating and preset and not preset["calibrated"] and not args.enforce)
        if preset:
            record.update(preset=args.preset, calibrated=preset["calibrated"], shadow=shadow)
        if shadow and not args.log:
            state = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "decisions"
            state.mkdir(parents=True, exist_ok=True, mode=0o700)
            args.log = str(state / (args.preset + ".jsonl"))
        url = endpoint()
        key = get_key(started + TIMEOUT)
        if args.check:
            print('{"configured":true,"network_checked":false}')
            return 0
        if args.input:
            with open(args.input, encoding="utf-8") as source:
                text = source.read(INPUT_LIMIT + 1)
        else:
            text = sys.stdin.read(INPUT_LIMIT + 1)
        require(len(text) <= INPUT_LIMIT, "input exceeds the API limit")
        record.update(input_length=len(text), input_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest())
        result = normalize(request({"model": MODEL, "input": text, "questions": questions},
                                   key, url, time.monotonic() + TIMEOUT), questions)
        matched = bool(gating and rule_passes(rule, result["answers"]))
        skip = matched and not shadow
        decision = "SKIP" if skip else "RUN"
        record.update(answers=result["answers"], usage=result["usage"], gate=decision if gating else None,
                      rule_passed=matched if gating else None,
                      elapsed_ms=round((time.monotonic() - started) * 1000))
        write_log(args.log, record, key)
        print(decision if gating else encode(result, key))
        return (0 if skip else RUN) if gating else 0
    except (Exception, KeyboardInterrupt) as error:
        reason = str(error) if isinstance(error, DecisionError) else "decision failed; check configuration and response format"
        record.update(gate="RUN", error=reason, elapsed_ms=round((time.monotonic() - started) * 1000))
        try:
            write_log(args.log if args else None, record, key)
        except DecisionError:
            reason = "cannot append decision log"
        print("RUN")
        print(reason.replace(key, "[REDACTED]") if key else reason, file=sys.stderr)
        return RUN


if __name__ == "__main__":
    sys.exit(main())
