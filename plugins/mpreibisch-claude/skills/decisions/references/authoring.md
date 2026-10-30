# Author a decision preset

Define one avoided operation before writing questions. A label is useful only when it selects a concrete cheaper branch.

- Name the required evidence and its boundaries, completeness, and relevant history.
- State the exact operation that `SKIP` avoids and the caller prerequisites for that branch.
- Define the expensive fallback for missing, conflicting, or uncertain evidence.
- Put critical semantics in question instructions. `input_template` guides preparation but is not sent to the API.
- Include an uncertainty choice when substantive choices otherwise force an answer. Keep uncertainty on the expensive path.
- Keep safety exclusions in `unless`; explicit threshold overrides retain these conditions.
- Start with `calibrated: false`. Thresholds are starting points until evaluated against independent local labels.

Caller-owned facts include authorization, budgets, scheduling, and whether an operation completed.
A classifier cannot establish these facts for the caller. Check them before calling Decisions.
Blank or whitespace-only input returns `RUN` without an API request. Other missing context relies on the questions and fallback.

## Bundled contracts

| Preset | Required evidence and caller prerequisites | Avoided operation and expensive fallback |
| --- | --- | --- |
| `progress-watch` | Goal, completion criteria, observation window, completeness, delivered work, errors, and intervention requests. The caller keeps scheduled full checks. | Skip one semantic watcher cycle. Otherwise run the full watcher; always check completion claims. |
| `review-triage` | Review bar, finding, diff context, user's handling policy, routine handling, and explicit prior history and disposition. Keep skipped findings recorded with later actions. | Skip this coordinator turn only when routine handling suffices. Otherwise run the coordinator, including for unresolved duplicates. |
| `failure-retry` | Operation, error, complete attempt history, authorization, remaining budget, elapsed required delay, replay safety, and known completion state. | Take the caller's bounded retry branch without diagnosis. Otherwise run diagnosis or escalation; a `RUN` never authorizes another retry. |
| `tier-routing` | Task, acceptance criteria, impact, ambiguities, and a caller-defined model capability mapping. An explicit user model choice takes precedence. | Skip frontier coordination for a supported cheaper tier. Otherwise use frontier or the user's chosen model under the existing workflow. |
| `relevance-filter` | Explicit information need, inclusion and exclusion criteria, candidate text, and supplied material boundaries. Include counterevidence. | Skip further summarization or synthesis of this supplied candidate. Otherwise process it through the existing workflow. No conclusion covers unseen source content. |

These cases describe intended behavior under enforcement. Shadow mode returns `RUN` for every case.
They specify the contract; they do not prove model accuracy.

| Preset | Confident skip | Required run | Missing or conflicting evidence |
| --- | --- | --- | --- |
| `progress-watch` | Complete ten-minute window shows useful delivered changes, clean checks, and no intervention request. Skip this cycle. | Agent claims done while required checks fail. Run the full watcher. | Partial logs omit part of the window. Use `insufficient_evidence` and run the watcher. |
| `review-triage` | A handled duplicate adds no facts, scope, or obligations. Policy permits recording it without a coordinator turn. | A duplicate blocker remains unresolved, or policy requires coordinator action on every finding. Run the coordinator. | Prior history or handling policy is unknown. Use `insufficient_evidence` and run the coordinator. |
| `failure-retry` | First read attempt hit explicit temporary capacity limits. Authorization, budget, elapsed delay, and replay safety are established. | The same failure recurs with `P(looping)=0.1`. Diagnose instead of retrying through this branch. | A write timed out with unknown completion. Use `insufficient_evidence` and diagnose its state. |
| `tier-routing` | A routine text change fits the caller's mapped small model, with explicit impact and ambiguity notes. | A bounded-looking change requires uncertain security reasoning. Use frontier. | Capability mapping or impact evidence is missing. Use frontier. Never override an explicit user model choice. |
| `relevance-filter` | A supplied recipe paragraph contributes nothing to a stated question about compiler diagnostics under explicit criteria. | An excerpt contradicts a proposed explanation of a compiler error. Keep it as relevant counterevidence. | The topic, criteria, or supplied boundaries are unclear. Use `insufficient_context` and retain the candidate. |

## External templates

The [example presets](../examples/README.md) are templates for `--preset-file`, outside the bundled catalog.
Define the handler or rubric before using them. Use a separate evaluation for label accuracy or model adequacy.
The [binary report](evaluation.md) only evaluates one defined skip decision.
