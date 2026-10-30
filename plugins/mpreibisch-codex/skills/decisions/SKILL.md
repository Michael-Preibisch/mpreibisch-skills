---
name: decisions
description: "Use the OpenAI Decisions API proactively whenever supplied text needs a bounded judgment with fixed answers: yes/no, one of several labels, or a score on a fixed scale. Especially use it to gate or replace an LLM sub-agent in polling, watching, triage, routing, or review-classification loops. Do not use it when answering requires tools or code reading, open-ended output, chained questions in one request, or high-stakes final calls."
---

# Decisions

Use the Decisions API for fixed questions over text you already have. Apply it without
asking when it fits the user's task and existing authorization. Supply the evidence;
the API cannot read files, use tools, or investigate missing context.
A wrapper that only runs a script and echoes its result needs no model: parse the line in code.

## Set up once

Use Python 3.10+. Set `OPENAI_API_KEY` in the host's environment through your secret store.
Alternatively, set `DECISIONS_KEY_CMD` to a command that prints only the key.
The script splits that command into arguments and runs it without a shell.
Pipes, shell expansion, and redirection are unsupported. The environment key takes precedence.
Never put a key in chat, command arguments, source files, or logs.

Resolve [scripts/decide.py](scripts/decide.py) relative to this installed skill directory.
Use its absolute path in workflows, independent of the current project.
Validate setup without reading stdin or calling the API:

```sh
python3 /ABSOLUTE/SKILL/DIRECTORY/scripts/decide.py --check
```

Replace `/ABSOLUTE/SKILL/DIRECTORY` with this skill's installed directory.
`--check` validates local configuration, not account access or key validity.
Run it separately from `--gate`.
If configuration is missing, continue the task with the LLM. Report setup once;
don't interrupt each iteration or silently install credentials.

## Choose a preset

Each preset contains fixed questions, an `input_template` note, a gate rule, and a `calibrated` field:

| Situation | Preset | Input | Cheaper branch selected by `SKIP` |
| --- | --- | --- | --- |
| Watching a background agent | [progress-watch](presets/progress-watch.json) | Goal, recent events, work delivered, and completion claims | Skip this LLM watcher cycle. |
| Triaging review findings | [review-triage](presets/review-triage.json) | Review bar, finding, diff hunk, and prior-round findings | Skip the coordinator turn for a non-blocker or duplicate. |
| Deciding to retry | [failure-retry](presets/failure-retry.json) | Error or recent verdicts, plus attempt history | Take the caller's bounded retry branch without LLM diagnosis. |
| Choosing a model tier | [tier-routing](presets/tier-routing.json) | Brief, touched files and lines, contract and security effects | Select the confident `small` or `standard` tier. |

Use `--preset NAME` to get normalized answers as JSON. Add bare `--gate` to apply its rule.
Omit `--input` to read stdin. Preset notes guide input preparation; they are not sent as evidence.
Preset questions cannot be combined with custom questions.

- `progress-watch`: requires `P(status=progressing) >= 0.9` and `P(quality_flag) < 0.2`.
  Its supplied replay covered 155 cycles, skipped 10.3%, and skipped none of 35 stalled or blocked cycles.
  The preset is marked calibrated for that replay; check performance on your own workflow.
  The caller can also skip an unchanged status that the LLM already handled.
  Keep one LLM pass per hour as a backstop.
- `review-triage`: requires `P(blocking) <= 0.05` or `P(same_as_prior=same_issue) >= 0.9`.
  A likely blocker, `P(blocking) >= 0.5`, always runs the coordinator, including duplicates.
  Do not treat missing context as proof that a finding is harmless.
- `failure-retry`: requires `P(failure_kind=transient_capacity_or_timeout) >= 0.9` and `P(looping) < 0.9`.
  For `P(looping) >= 0.9`, stop patching and escalate to the coordinator or human.
- `tier-routing`: requires `P(tier=small) >= 0.85` or `P(tier=standard) >= 0.85`.
  Otherwise, use the stronger `frontier` tier.

For retry escalation or tier selection, omit `--gate` and read `answers` in the JSON output.
Predicates expose true and false probabilities. Choice answers include the selected `value`.
Gate logs retain these answers too. A classification never authorizes an external action.

## Gate an expensive step

Skip only a confident routine answer. Run the LLM for every other result:

```text
Existing evidence -> Decisions API -> Rule passes and enforcement enabled? -> SKIP
                                      Shadow, uncertainty, or any error    -> RUN
```

This shell step uses the watcher preset:

```sh
if python3 /ABSOLUTE/SKILL/DIRECTORY/scripts/decide.py \
  --input events.txt --preset progress-watch --gate \
  --log decisions.jsonl
then
  : # Skip this watcher cycle.
else
  run_llm_watcher
fi
```

Replace `run_llm_watcher` with the workflow's existing expensive step.
Repeat `--gate CONDITION` for custom conditions joined with AND.
Explicit conditions replace the preset's thresholds but retain its `unless` guards for blockers and loops.
Preset rules use `all` for AND, `any` for OR, and `unless` for conditions that forbid skipping.
Conditions support `<`, `<=`, `>`, and `>=`.
For choices, compare `NAME=VALUE` probabilities. For predicates, compare `NAME` directly
against the true probability. Score conditions use `NAME=LABEL`.
Boolean choices use lowercase `true` or `false`; ambiguous names or options fail open.
Gate mode prints `SKIP` and exits `0` only when its rule passes and shadow mode is off.
Otherwise, it prints `RUN` and exits `10`. Any error also prints `RUN` with a reason on stderr.
Use the exit code to fall back, including when the interpreter or script cannot start.

## Calibrate before skipping

Presets with `calibrated: false` always print `RUN` in gate mode unless you pass `--enforce`.
They still classify and log the answer, with `shadow: true` and the proposed `rule_passed` value.
Use `--log FILE` to choose a private JSONL log. Otherwise, shadow logs go to
`$XDG_STATE_HOME/decisions/NAME.jsonl`, defaulting to `~/.local/state/decisions/NAME.jsonl`.
Replace `NAME` with the preset name. A log failure runs the LLM.

Keep the LLM running while collecting shadow results. Log its answers beside the decision records using the input hash.
Label representative examples from actual evidence and compare disagreements.
After validating thresholds, set the preset's `calibrated` field to `true`, or pass `--enforce` explicitly.
Plugin updates can replace local preset edits. Recheck calibration after changing questions, options, rules, or workflow evidence.
For custom gates, run the LLM regardless of the exit code until labeled examples support enforcement.

`--log FILE` appends one JSONL record per call, including failures after argument parsing.
It records input length and SHA-256, normalized answers, usage, elapsed time, and the gate result.
It excludes the key and full input. Store logs privately. A log failure also runs the LLM.
`--check` does not create a decision log.

## Custom questions

If no preset fits, use `--questions FILE` with the API's JSON question array.
Use predicates for yes/no, choices for labels, and ordered score levels for a fixed scale.
Give options one-line descriptions and keep option sets fixed.
Ask independent questions together; dependent questions need separate requests.

`--predicate NAME INSTRUCTIONS` adds a predicate.
`--choice NAME INSTRUCTIONS CHOICES_JSON` adds a choice using the API's option array.
File questions come first, then predicates, then choices. Names must be unique;
unnamed file questions receive names such as `question_1`.
Default output contains names, types, selected values, probabilities, model, and usage.

## Cost and failures

As of October 29, 2026, the [API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create)
lists `gpt-6-luna` at $0.10 per million uncached input tokens, with free output.
The [Decisions guide](https://developers.openai.com/api/docs/guides/decisions)
describes fixed questions and probability thresholds. Measure latency in your own
workflow using `elapsed_ms`; no latency guarantee is assumed.

The script retries HTTP `429` and `5xx` responses twice with short backoff.
The HTTP exchange has a 5-second overall deadline. Key commands have a separate
5-second deadline. Missing credentials, timeouts, HTTP errors, refusals, malformed
answers, invalid gates, and logging errors all fall back to the LLM.
It never prints HTTP bodies, key-command diagnostics, or exception details.
`DECISIONS_BASE_URL` exists only for offline tests and accepts a loopback HTTP server.
Never send private text beyond the user's existing data-sharing authorization.
