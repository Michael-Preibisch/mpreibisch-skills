from contextlib import redirect_stderr, redirect_stdout
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import uuid


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/mpreibisch-codex/skills/decisions/scripts/decide.py"
SPEC = importlib.util.spec_from_file_location("decide", SCRIPT)
decide = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(decide)
QUESTIONS = [
    {"type": "choice", "name": "status", "instructions": "Classify the supplied build events.",
     "choices": [{"value": "progressing", "description": "Successful steps advance."},
                 {"value": "blocked", "description": "A failure prevents progress."}]},
    {"type": "predicate", "name": "quality_flag", "instructions": "Do the events show failed checks?"},
]


def response(progress=0.95, flag=0.1):
    return {"model": "gpt-6-luna", "answers": [
        {"type": "choice", "name": "status", "choice": "progressing" if progress >= 0.5 else "blocked",
         "confidence": max(progress, 1 - progress),
         "probabilities": [{"value": "progressing", "probability": progress},
                           {"value": "blocked", "probability": 1 - progress}]},
        {"type": "predicate", "name": "quality_flag", "probability": flag}],
        "usage": {"input_tokens": 100, "output_tokens": 0, "total_tokens": 100,
                  "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                  "output_tokens_details": {}}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        size = int(self.headers["Content-Length"])
        self.server.requests.append((self.path, json.loads(self.rfile.read(size))))
        if self.server.disconnect:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        statuses = self.server.statuses
        status = statuses.pop(0) if len(statuses) > 1 else statuses[0]
        payload = self.server.payload
        raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        time.sleep(self.server.delay)
        try:
            self.send_response(status)
            self.end_headers()
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="decisions-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.questions = self.root / "questions.json"
        self.questions.write_text(json.dumps(QUESTIONS), encoding="utf-8")
        self.log = self.root / "decisions.jsonl"
        self.secret = "test-" + uuid.uuid4().hex
        self.env = {name: value for name, value in os.environ.items()
                    if name not in {"OPENAI_API_KEY", "DECISIONS_KEY_CMD", "DECISIONS_BASE_URL"}}
        self.env.update(OPENAI_API_KEY=self.secret,
                        DECISIONS_BASE_URL="http://127.0.0.1:0/v1", XDG_STATE_HOME=str(self.root / "state"))

    def call(self, *args, input_text="Successful build step.", script=SCRIPT):
        try:
            result = subprocess.run([sys.executable, str(script), *args], input=input_text,
                                    capture_output=True, text=True, env=self.env, cwd=self.root, timeout=8)
        except subprocess.TimeoutExpired:
            raise AssertionError("decision command timed out") from None
        surfaces = [result.stdout, result.stderr]
        if self.log.is_file():
            surfaces.append(self.log.read_text(encoding="utf-8"))
        # A failed assertion must not reproduce the credential in the test report.
        self.assertTrue(all(self.secret not in surface for surface in surfaces), "credential leaked")
        return result

    def gate(self, *args):
        return self.call("--questions", str(self.questions), "--gate", "status=progressing>=0.9",
                         "--gate", "quality_flag<0.2", "--log", str(self.log), *args)

    def assert_run(self, result):
        self.assertEqual(result.returncode, 10)
        self.assertEqual(result.stdout, "RUN\n")


class ConfigurationTests(Fixture):
    def test_missing_key_and_key_command_failure_fail_open(self):
        del self.env["OPENAI_API_KEY"]
        self.assert_run(self.gate())
        self.env["DECISIONS_KEY_CMD"] = shlex.join([sys.executable, "-c", "raise SystemExit(1)"])
        self.assert_run(self.gate())

    def test_check_uses_key_command_without_network_and_survives_relocation(self):
        del self.env["OPENAI_API_KEY"]
        self.env["DECISIONS_TEST_SECRET"] = self.secret
        command = self.root / "read key.py"
        command.write_text("import os, sys\nprint(os.environ['DECISIONS_TEST_SECRET'])\n"
                           "print(os.environ['DECISIONS_TEST_SECRET'], file=sys.stderr)\n", encoding="utf-8")
        self.env["DECISIONS_KEY_CMD"] = shlex.join([sys.executable, str(command)])
        for host in ("codex", "claude"):
            package = ROOT / "plugins" / ("mpreibisch-" + host)
            relocated = self.root / host
            shutil.copytree(package / "skills/decisions", relocated)
            result = self.call("--preset", "progress-watch", "--check", script=relocated / "scripts/decide.py")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), {"configured": True, "network_checked": False})
        self.env["OPENAI_API_KEY"] = self.secret
        self.env["DECISIONS_KEY_CMD"] = "missing-key-reader"
        self.assertEqual(self.call("--check").returncode, 0)

    def test_invalid_gates_and_arguments_fail_open(self):
        for condition in ("status=missing>=0.9", "quality_flag<2", "status>=0.9", "missing<0.2"):
            with self.subTest(condition=condition):
                self.assert_run(self.call("--questions", str(self.questions), "--gate", condition))
        self.assert_run(self.call("--unknown", self.secret))
        self.assert_run(self.call("--questions", str(self.questions), "--gate", "quality_flag<0.2", "--check"))


class DecisionLogicTests(unittest.TestCase):
    def test_documented_rule_checks_both_probabilities_and_rejects_invalid_answers(self):
        gates = decide.parse_gates(["status=progressing>=0.9", "quality_flag<0.2"], QUESTIONS)
        for progress, flag, expected in [(0.9, 0.19, True), (0.95, 0.2, False),
                                         (0.89, 0.1, False), (0.1, 0.05, False)]:
            with self.subTest(progress=progress, flag=flag):
                result = decide.normalize(response(progress, flag), QUESTIONS)
                self.assertEqual(decide.should_skip(gates, result["answers"]), expected)
        refusal = response()
        refusal["answers"][1] = {"type": "refusal", "name": "quality_flag"}
        malformed = response()
        malformed["answers"][0]["probabilities"].pop()
        for payload in (refusal, malformed, {}):
            with self.assertRaises(decide.DecisionError):
                decide.normalize(payload, QUESTIONS)


class PresetTests(Fixture):
    def invoke(self, name, *flags, probabilities=None):
        preset = json.loads((SCRIPT.parent.parent / "presets" / (name + ".json")).read_text())
        payload = response()
        payload["answers"] = []
        for question in preset["questions"]:
            answer = {"type": question["type"], "name": question["name"]}
            if question["type"] == "predicate":
                answer["probability"] = (probabilities or {}).get(question["name"], 0.01)
            else:
                choices = question["choices"]
                answer.update(choice=choices[0]["value"], confidence=0.98,
                              probabilities=[{"value": option["value"],
                                              "probability": 0.98 if index == 0 else 0.02 / (len(choices) - 1)}
                                             for index, option in enumerate(choices)])
            payload["answers"].append(answer)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, self.env, clear=True), \
                patch.object(sys, "argv", [str(SCRIPT), "--preset", name, *flags]), \
                patch.object(sys, "stdin", io.StringIO("Supplied workflow evidence.")), \
                patch.object(decide, "request", return_value=payload) as transport, \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = decide.main()
        surfaces = [stdout.getvalue(), stderr.getvalue()]
        surfaces.extend(path.read_text() for path in self.root.rglob("*.jsonl"))
        self.assertTrue(all(self.secret not in surface for surface in surfaces), "credential leaked")
        return subprocess.CompletedProcess([], code, stdout.getvalue(), stderr.getvalue()), transport

    def test_preset_loading_sends_only_documented_api_fields(self):
        for name, names in [("progress-watch", ["status", "quality_flag"]),
                            ("review-triage", ["blocking", "same_as_prior"]),
                            ("failure-retry", ["failure_kind", "looping"]), ("tier-routing", ["tier"])]:
            with self.subTest(preset=name):
                result, transport = self.invoke(name)
                self.assertEqual(result.returncode, 0)
                body = transport.call_args.args[0]
                self.assertEqual(set(body), {"model", "input", "questions"})
                self.assertEqual(body["model"], "gpt-6-luna")
                self.assertEqual(body["input"], "Supplied workflow evidence.")
                self.assertEqual([question["name"] for question in body["questions"]], names)
                self.assertEqual(body["questions"], decide.load_preset(name)["questions"])
                self.assertEqual([answer["name"] for answer in json.loads(result.stdout)["answers"]], names)
        self.assert_run(self.call("--preset", "missing-preset", "--gate"))
        self.assert_run(self.call("--preset", "../progress-watch", "--gate"))
        self.assert_run(self.call("--gate"))

    def test_shadow_logs_candidates_enforcement_preserves_blocker_and_loop_guards(self):
        for name in ("review-triage", "failure-retry", "tier-routing"):
            with self.subTest(preset=name):
                result, _ = self.invoke(name, "--gate")
                self.assert_run(result)
                path = self.root / "state/decisions" / (name + ".jsonl")
                record = json.loads(path.read_text())
                self.assertTrue(record["shadow"])
                self.assertTrue(record["rule_passed"])
                self.assertEqual(record["gate"], "RUN")
                result, _ = self.invoke(name, "--gate", "--enforce", "--log", str(self.log))
                self.assertEqual((result.returncode, result.stdout), (0, "SKIP\n"))
        result, _ = self.invoke("progress-watch", "--gate")
        self.assertEqual((result.returncode, result.stdout), (0, "SKIP\n"))
        for blocking in (0.5, 0.95):
            for condition in ([], ["same_as_prior=same_issue>=0.9"]):
                result, _ = self.invoke("review-triage", "--gate", *condition, "--enforce",
                                        probabilities={"blocking": blocking})
                self.assert_run(result)
        result, _ = self.invoke("failure-retry", "--gate", "--enforce", probabilities={"looping": 0.9})
        self.assert_run(result)


class DecisionsTests(Fixture):
    @classmethod
    def setUpClass(cls):
        try:
            cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        except PermissionError:
            raise unittest.SkipTest("the sandbox forbids binding the local HTTP stub") from None
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        super().setUp()
        self.env["DECISIONS_BASE_URL"] = f"http://127.0.0.1:{self.server.server_port}/v1"
        self.server.requests = []
        self.server.statuses = [200]
        self.server.payload = response()
        self.server.delay = 0
        self.server.disconnect = False

    def test_gate_requires_every_condition_and_respects_boundaries(self):
        for progress, flag, expected in [(0.9, 0.19, "SKIP"), (0.95, 0.2, "RUN"),
                                         (0.89, 0.1, "RUN"), (0.1, 0.05, "RUN")]:
            with self.subTest(progress=progress, flag=flag):
                self.server.payload = response(progress, flag)
                result = self.gate()
                self.assertEqual(result.stdout, expected + "\n")
                self.assertEqual(result.returncode, 0 if expected == "SKIP" else 10)
        records = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual([record["gate"] for record in records], ["SKIP", "RUN", "RUN", "RUN"])
        self.assertEqual(records[0]["input_sha256"], hashlib.sha256(b"Successful build step.").hexdigest())
        self.assertNotIn("Successful build step.", self.log.read_text())

    def test_http_refusal_and_malformed_answers_fail_open_without_echoing_bodies(self):
        refusal = response()
        refusal["answers"][1] = {"type": "refusal", "name": "quality_flag"}
        invalid_probability = response()
        invalid_probability["answers"][1]["probability"] = float("nan")
        missing_option = response()
        missing_option["answers"][0]["probabilities"].pop()
        inconsistent_choice = response()
        inconsistent_choice["answers"][0]["choice"] = "blocked"
        for status, payload in [(400, {"message": self.secret}), (429, {"message": self.secret}),
                                (503, {"message": self.secret}), (200, refusal),
                                (200, b"not JSON"), (200, {}), (200, invalid_probability),
                                (200, missing_option), (200, inconsistent_choice)]:
            with self.subTest(status=status, body_type=type(payload).__name__):
                self.server.statuses = [status]
                self.server.payload = payload
                before = len(self.server.requests)
                result = self.gate()
                self.assert_run(result)
                self.assertTrue(result.stderr)
                self.assertEqual(len(self.server.requests) - before, 3 if status in (429, 503) else 1)

    def test_retries_transient_errors_then_classifies(self):
        self.server.statuses = [429, 503, 200]
        result = self.gate()
        self.assertEqual((result.returncode, result.stdout), (0, "SKIP\n"))
        self.assertEqual(len(self.server.requests), 3)

    def test_disconnect_and_slow_server_fail_open_within_deadline(self):
        self.server.disconnect = True
        self.assert_run(self.gate())
        self.server.disconnect = False
        self.server.delay = 5.5
        started = time.monotonic()
        self.assert_run(self.gate())
        self.assertLess(time.monotonic() - started, 6.5)

    def test_shorthand_builds_documented_body_and_redacts_outputs_and_logs(self):
        payload = response()
        payload["answers"].reverse()
        payload["usage"]["echo"] = self.secret
        self.server.payload = payload
        result = self.call("--predicate", "quality_flag", QUESTIONS[1]["instructions"],
                           "--choice", "status", QUESTIONS[0]["instructions"],
                           json.dumps(QUESTIONS[0]["choices"]), "--log", str(self.log),
                           input_text="Build events " + self.secret)
        self.assertEqual(result.returncode, 0)
        path, body = self.server.requests[0]
        self.assertEqual(path, "/v1/decisions")
        self.assertEqual(body["model"], "gpt-6-luna")
        self.assertTrue(body["input"] == "Build events " + self.secret, "input changed")
        self.assertEqual(body["questions"], [QUESTIONS[1], QUESTIONS[0]])
        output = json.loads(result.stdout)
        self.assertEqual([answer["value"] for answer in output["answers"]], [False, "progressing"])
        self.assertEqual(output["usage"]["echo"], "[REDACTED]")
        self.assertIsNone(json.loads(self.log.read_text())["gate"])

    def test_log_errors_never_skip(self):
        self.assert_run(self.gate("--log", str(self.root / "missing" / "log.jsonl")))
        self.assertEqual(len(self.server.requests), 1)

    def test_file_questions_include_scores_and_boolean_choices(self):
        questions = [
            {"type": "score", "name": "severity", "instructions": "Rate the supplied issue.",
             "levels": [{"label": "low", "description": "Cosmetic."},
                        {"label": "high", "description": "Prevents use."}]},
            {"type": "choice", "name": "routine", "instructions": "Is this routine?",
             "choices": [{"value": True}, {"value": False}]},
        ]
        self.questions.write_text(json.dumps(questions), encoding="utf-8")
        payload = response()
        payload["answers"] = [
            {"type": "score", "name": "severity", "score": 0.05, "confidence": 0.95,
             "probabilities": [{"label": "low", "value": 0, "probability": 0.95},
                               {"label": "high", "value": 1, "probability": 0.05}]},
            {"type": "choice", "name": "routine", "choice": True, "confidence": 0.99,
             "probabilities": [{"value": True, "probability": 0.99}, {"value": False, "probability": 0.01}]}]
        self.server.payload = payload
        input_file = self.root / "events.txt"
        input_file.write_text("Build complete.", encoding="utf-8")
        result = self.call("--questions", str(self.questions), "--input", str(input_file),
                           "--gate", "severity=low>0.9", "--gate", "routine=true>=0.9")
        self.assertEqual((result.returncode, result.stdout), (0, "SKIP\n"))
        self.assertEqual(self.server.requests[0][1]["questions"], questions)
        self.assertEqual(self.server.requests[0][1]["input"], "Build complete.")


if __name__ == "__main__":
    unittest.main()
