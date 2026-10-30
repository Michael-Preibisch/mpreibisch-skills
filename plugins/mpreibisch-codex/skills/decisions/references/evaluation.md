# Evaluate local shadow decisions

Keep project questions and thresholds in an ordinary JSON preset outside the installed plugin.
Use the bundled format: `questions`, `input_template`, `gate`, and boolean `calibrated`.
Start with `calibrated: false`, as every bundled preset does. Historical replay results are example evidence, not local calibration.
An explicit `--gate CONDITION` replaces the preset rule's thresholds and defaults to shadow unless you pass `--enforce`.
This applies even when an external preset says `calibrated: true`; its `unless` exclusions remain in effect.

Record a proposed gate result while the existing expensive step still runs:

```sh
python3 /ABSOLUTE/SKILL/DIRECTORY/scripts/decide.py --preset-file local-preset.json \
  --input evidence.txt --gate --shadow --id item-1 --log decisions.jsonl
```

Replace `/ABSOLUTE/SKILL/DIRECTORY` with the installed skill directory.
Replace `item-1` with the caller's identifier for this evidence and independently checked outcome.
`--shadow` overrides enforcement and always prints `RUN`, including on errors.
The existing step must still run. For a report, give each item a unique ID within a configuration.
The same ID can compare configurations against the same independent outcome.
Pass `--id` and a dedicated `--log` per workflow when you plan to run `report`.

Logs omit full input and credentials. They record normalized answers, `rule_passed`, actual gate output, input hash, and usage.
Configuration provenance contains `model`, `questions_sha256`, `preset_sha256`, `gate_rule`, and `config_sha256`.
Successful calls record the returned model name; failed calls retain the requested model.
Changes to a preset, questions, rule, or model produce separate configuration groups.

## Supply independent labels

Use JSONL with one independently checked outcome per ID:

```json
{"id":"item-1","needed":true}
{"id":"item-2","needed":false}
```

`needed: true` means the expensive step was needed for that evidence.
Check outcomes against the actual task and evidence. An old LLM verdict is a disagreement signal, not automatic ground truth.
Do not copy a gate's own answer into its label.

The binary label evaluates one defined choice between an expensive step and its cheaper branch.
It does not validate routing labels, score rubrics, or the adequacy of a selected model tier.

| Tier example | Result |
| --- | --- |
| A task needs `standard` but not `frontier`. | A label for whether frontier is needed is `needed: false`. |
| The classifier selects `small` and proposes skipping frontier. | The binary report can count this as a safe proposed skip. |
| The selected `small` model is inadequate. | The binary report has not established tier adequacy. Check it with route-specific outcomes. |

Define the avoided operation when labeling. A low unsafe-skip count cannot establish general routing accuracy.

Generate the offline report:

```sh
python3 /ABSOLUTE/SKILL/DIRECTORY/scripts/decide.py report --log decisions.jsonl --labels labels.jsonl
```

The report reads files only. It needs no API key and makes no network call.
It joins by `id`, not input hash or line position. It rejects duplicate label IDs and duplicate IDs within a configuration.
Records without a usable ID are skipped and counted as `unjoinable`.
Pre-configuration failures count toward the top-level `errors` total without entering a configuration group.
Other joined records require gate configuration provenance; malformed records fail the report.
Report failures print a message on stderr and exit `2`, with no `RUN` output or changes to the source log.

Each configuration reports these fields:

| Field | Meaning |
| --- | --- |
| `proposed_skips` | Successful answers whose recorded rule passes, including shadow records that printed `RUN`. |
| `unsafe_proposed_skips` | Proposed skips whose independent label says the expensive step was needed. |
| `unlabeled_proposed_skips` | Proposed skips without an independent label; their safety is unknown. |
| `records`, `labeled_records`, `unlabeled_records`, `errors` | Coverage and failures, including records without a usable answer. |
| `main_condition` | First condition in `all`, or first in `any` when `all` is empty. |
| `thresholds` | Proposed and unsafe skip counts at each displayed threshold for that condition. |

Threshold rows vary only the main condition's threshold. Other conditions and safety guards stay fixed.
The grid is fixed and includes the recorded threshold. No threshold is selected, fitted, or written back to a preset.
`unmatched_labels` counts label IDs absent from the logs.
Top-level `errors` counts all error records, including unjoinable ones; a record can contribute to both totals.
Missing labels and API failures are not evidence of safety.

A recorded `SKIP` is not proof an expensive turn was avoided. Check the caller's actual branch execution separately.
After choosing a threshold, evaluate it on separate labeled examples before enabling enforcement.
No finite replay establishes a zero-miss guarantee. Promotion remains an explicit caller decision.
