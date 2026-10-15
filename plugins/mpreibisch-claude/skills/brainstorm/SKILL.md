---
name: brainstorm
description: Brainstorm with the other model. Both generate ideas independently, then build on and challenge each other's ideas, and rank them against the user's criteria while keeping dissent. Use to brainstorm together, generate alternatives, or explore options with Codex or Claude Code; not for reaching agreement.
---

# Brainstorm

Brainstorming aims for range, then a ranked shortlist. It never requires agreement;
use `consensus` for that. Read [the handoff protocol](../../bridge/protocol.md) and
[CLI instructions](../../bridge/cli.md). The calling/main agent must supply the broader
goal, motivations, constraints, decision rationale, and intended outcome on every call,
plus the user's ranking criteria. A topic alone is not enough. Both agents stay read-only.

Use one session file for the whole brainstorm (`--session-file "$HANDOFF/session.json"`),
so the peer keeps its ideas and reasoning between turns. Each request uses phase `single`.

1. **Frame.** State the problem, what a good idea must achieve, hard constraints, ideas
   already rejected and why, and the ranking criteria. Default to three calls; the user
   can ask for more.
2. **Write your own ideas first.** Save them in `main-ideas-0.md` before you read the
   peer's output. Keep the file outside the peer's read scope.
3. **Call 0: the peer's ideas, blind.** Send the framing without your ideas. Ask for
   ideas with what each is, why it might work, its key assumption, and its falsifier.
4. **Call 1: cross-pollinate.** Resume the session and send your ideas. Ask the peer to
   build on, combine, and challenge both lists, add ideas both missed, and say what to drop.
   Do the same with its list yourself.
5. **Rank.** Rank the merged list against the user's criteria. Optionally resume once more
   (call 2) for the peer's ranking and dissent.
6. **Hand back** a shortlist: each idea with its rationale, key assumption, falsifier, and
   origin (you, the peer, or combined). Keep every unresolved disagreement and both views.
   Name what would settle it. Don't implement the ideas as part of this skill.

The response uses the exploration format: one idea per entry in `recommendations`, and
the full list, reactions, and ranking in the Markdown `artifact`. Judge the ideas
yourself. A confident peer is still one opinion.
