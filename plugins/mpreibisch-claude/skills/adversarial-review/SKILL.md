---
name: adversarial-review
description: Ask the other model to challenge a plan, implementation or PR, or idea with evidence-based findings ranked by severity. Use for a second opinion, to challenge a plan, to find holes in a design or diff, or for any critical second-model review without code changes.
---

# Adversarial review

Read [the handoff protocol](../../bridge/protocol.md) and
[CLI instructions](../../bridge/cli.md). The calling/main agent must provide the
broader goal, motivations, constraints, decision rationale, and intended outcome.
Do not forward only a diff, plan, or idea. Both agents remain read-only; do not fix
code, reformat files, apply patches, or run tests that write project artifacts.

If the user asks for receiver sub-agents, set `subagents` in the request (see
[Sub-agents](../../bridge/cli.md#sub-agents)). For example, Claude asks Codex Astra xhigh
with Terra 6.1 high sub-agents (`{"model": "gpt-6.1-terra", "effort": "high"}`), or Codex
asks Claude Opus 5.5 high with Sonnet 5.5 high sub-agents
(`{"model": "claude-sonnet-5-5", "effort": "high"}`). Sub-agents stay read-only.

1. Identify the review target and its stable snapshot: plan text, idea, commit range,
   implementation files, or PR diff plus relevant surrounding code. Define read paths,
   exclusions, and expected findings. Include the intended behavior and alternatives
   already considered, so the critique addresses the actual problem.
2. Send a bounded challenge assignment through the other model's CLI. Prioritize
   invalid assumptions, correctness flaws, missing cases, security or data risks,
   operational failure, compatibility, and simpler alternatives. Assess whether the
   proposed work solves the broader goal. Do not invent defects to meet a quota.
3. Require each finding to identify its severity, title, location, triggering scenario,
   evidence IDs, consequence, recommended action or alternative, and confidence.
   Distinguish verified defects from uncertain risks. A preference without a concrete
   consequence is not a defect. State evidence that would disprove uncertain findings.
4. Inspect the findings and cited evidence. Classify the main agent's disposition as
   accepted, disputed, or needing evidence, with a concise rationale. Preserve valid
   criticism even when it challenges the original plan. Return empty findings if no
   supported issue exists; state coverage limits instead of inventing assurance.
5. **Follow-ups in the same session.** Pass the same `--session-file` so the reviewer
   keeps its context. For disputed findings, resume once with your rationale and
   evidence; the reviewer withdraws the finding or adds evidence. After fixes, resume
   with the new snapshot for a re-review of every earlier finding and of the fix itself.
   For a fully independent second review, use a new session file, never a fork.

Severity levels are defined in the [receiver brief](../../bridge/receivers/adversarial-review.md).
The result uses `responses/adversarial-review.schema.json`: ranked `findings`,
`coverage`, `alternatives`, shared evidence, and uncertainties. Include file/line
references or exact plan sections. Return scoped observations, not an unqualified
"safe" or "approved" verdict. The main agent hands back findings and dispositions;
implementation is a separate authorized task.
