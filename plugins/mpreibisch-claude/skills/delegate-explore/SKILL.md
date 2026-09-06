---
name: delegate-explore
description: Delegate a bounded research or codebase-exploration lane to the other model, with an explicit question, scope, and evidence-backed artifact. Use for exploration without implementation changes.
---

# Delegate exploration

Read [the handoff protocol](../../bridge/protocol.md) and
[CLI instructions](../../bridge/cli.md). The calling/main agent must provide the
broader goal, motivations, constraints, decision rationale, and intended outcome.
Explain how this exploration supports the broader goal. A search query or file list
alone is insufficient. Both agents remain read-only, including verification commands.

1. Choose one bounded lane with a clear question. Name its read paths or supplied
   sources, exclusions, evidence snapshot, time budget, and expected artifact. Examples
   include a call graph, dependency map, comparison of supplied sources, or an answer
   with file/line evidence. State the decision this research will inform.
2. Include known facts, relevant project conventions, prior hypotheses, and unresolved
   questions. Label hypotheses so the delegate can challenge them. Give completion
   criteria, such as tracing all callers within named directories or comparing three
   specified options against stated constraints.
3. Call the other model with a `delegate-explore` request. Require observations,
   evidence, uncertainties, recommendations, and a coverage summary. Distinguish
   "not found in this scope" from "does not exist". No edits, dependency installs,
   generated code, mutating tests, or external actions.
4. Validate the returned evidence and incorporate the relevant findings into the
   broader task. Mark unanswered questions and limited coverage. If the lane is too
   large or blocked, request a narrower artifact or report the missing source; do
   not let the delegate silently expand scope.

Use `responses/delegate-explore.schema.json`. Each observation has a claim and
evidence IDs; each recommendation explains its rationale and connection to the goal.
The `artifact` contains the requested map, comparison, or research note in Markdown.
For web research, the default helper consumes supplied source snapshots; the main
agent can retrieve authorized public sources with its available tools and pass their
contents and citations. Missing live access is a coverage limit, never permission
to enable an unbounded network or external tools.
