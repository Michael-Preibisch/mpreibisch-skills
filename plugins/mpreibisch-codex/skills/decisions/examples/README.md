# External preset templates

These files are templates for `--preset-file`, not bundled presets for `--preset`.
Copy a template outside the plugin and adapt it to the caller's workflow. Both start in shadow mode.

| Template | Required local definition | Cheaper branch and fallback |
| --- | --- | --- |
| [request-routing.json](request-routing.json) | Categories, matching choices, complete handler scopes, and fallback. The example uses `question`, `change`, and `incident`. | Read `answers` or gate logs to select the configured handler. Uncertainty retains the expensive routing pass. |
| [severity-score.json](severity-score.json) | An impact rubric matching the score levels, routine handling, and a separate urgency policy. | A supported low-impact result can avoid an expensive triage pass. Missing evidence or an unmet obligation retains it. |

Severity measures impact. Urgency measures time sensitivity. A small defect can have an urgent deadline; handle that obligation separately.
The score template includes a predicate because a score alone cannot express insufficient evidence.
Ignore the score when the evidence or rubric is insufficient. Keep the expensive fallback.

```sh
python3 /ABSOLUTE/SKILL/DIRECTORY/scripts/decide.py --preset-file local-routing.json \
  --input request.txt --gate --shadow --id request-1 --log routing.jsonl
```

Replace the paths with the installed script, your adapted preset, and the supplied request.
A `SKIP` only avoids the defined expensive pass. It never authorizes the selected handler's actions.

| Template | Confident skip | Required run | Missing or conflicting evidence |
| --- | --- | --- | --- |
| Request routing | An information request fits the complete question handler scope. | A mixed incident and change request exceeds every handler's scope. | Handler limits are missing. Use `insufficient_context` and the routing fallback. |
| Severity score | A cosmetic issue meets the caller's low rubric and routine handling satisfies all obligations. | Essential function is unavailable under the caller's high rubric. | Impact evidence conflicts or the rubric is absent. Ignore the score and run triage. |

The [authoring contract](../references/authoring.md) defines prerequisites and evidence requirements.
The [binary report](../references/evaluation.md) cannot validate routing labels or an impact rubric.
