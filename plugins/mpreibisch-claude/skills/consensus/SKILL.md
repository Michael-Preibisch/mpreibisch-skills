---
name: consensus
description: Reach a reasoned Codex and Claude Code consensus on a question, plan, decision, or diff through independent assessments and bounded disagreement resolution. Use when a second model's agreement or an explicit split decision is needed.
---

# Consensus

The calling agent coordinates; the other model is an independent peer. Read
[the handoff protocol](../../bridge/protocol.md) and [CLI instructions](../../bridge/cli.md).
The calling/main agent must supply the broader goal, motivations, constraints,
decision rationale, and intended outcome on every call. A question or diff alone
is not enough. Both agents remain read-only, except for caller-owned scratch artifacts.

## Independent assessment

1. Define the exact question, evidence snapshot, scope, expected decision artifact,
   and decision criteria. Set `MAX_ROUNDS` from the user, default `3`; it must be a
   positive integer. Store it as `exchange.max_rounds`.
2. Record the main agent's position in `main-position-0.json` before reading any peer
   response. Use the consensus response schema: conclusion, assumptions, supporting
   evidence IDs, confidence, alternatives, and disagreements. Do not send this position
   to the peer yet. Keep it outside the peer's read scope.
3. Send the same context and evidence to the peer with `phase: "assess"`, `round: 0`,
   `positions: []`, and `candidate_conclusion: ""`. Decision rationale describes the
   task's existing choices, not the main agent's new assessment. The peer must form
   its own position without seeing the main agent's proposed answer. Reviewing an
   existing plan/diff necessarily includes that shared input.
4. Save the peer's independent position. Check its evidence and completeness. The
   initial assessments are round zero and do not count toward `MAX_ROUNDS`.

## Resolve disagreements

For each exchange round from `1` through `MAX_ROUNDS`:

1. Compare the two positions. Give each disagreement a stable ID. Separate factual
   disputes, assumption differences, and tradeoffs. Cite evidence and state what
   observation or constraint would resolve each difference.
2. The main agent writes its updated structured position, addressing the peer's
   claims. Record changed beliefs and remaining objections. Form an exact candidate
   conclusion only when the main agent can endorse it.
3. Send the full context, evidence, both latest attributed positions, disagreement
   IDs, and that candidate to the peer with `phase: "exchange"` and the current round.
   The peer addresses each objection, updates its position, and returns
   `agrees_with_candidate` and the exact `candidate_conclusion`. Agreement must be
   explicit; politeness, partial overlap, silence, or a revised candidate is insufficient.
4. Check the peer's changes and any new evidence. End early only if both agents endorse
   the identical conclusion, the peer is `complete`, and no material disagreement
   remains. If the peer changes the candidate, the main agent must evaluate it and
   obtain explicit mutual endorsement within the remaining rounds. Never call a
   majority vote or an unsupported compromise consensus.

One round is one main-agent revision followed by one peer response. Do not start
another round beyond the configured cap. No hidden tie-breaker calls. If evidence
changes the question or scope, report that and obtain the needed context rather
than quietly restarting the counter. Stop early on blocking failures or if both
agents agree a remaining choice requires human judgment.

## Final artifact

Write `decision.json` with `status` (`consensus` or `split_decision`), the question,
context summary, `max_rounds`, `rounds_used`, conclusion, both final positions,
evidence references, resolved and unresolved disagreement IDs, and
`human_arbitration_required`.

For consensus, identify both explicit endorsements and the exact shared conclusion.
For a split decision, preserve each position, the strongest evidence for it, and the
specific human choice or missing evidence required. Set `human_arbitration_required`
to true. A missing/failed peer is an unestablished position, never a fabricated view.
Report a split decision with the failure and available position. Do not implement
the conclusion as part of this skill.
