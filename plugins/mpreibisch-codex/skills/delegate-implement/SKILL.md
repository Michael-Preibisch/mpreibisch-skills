---
name: delegate-implement
description: Delegate a concrete, testable implementation specification to the other model with bounded write scope, acceptance criteria, and a verified handoff. Use to have the other CLI agent implement an authorized, scoped specification.
---

# Delegate implementation

Read [the handoff protocol](../../bridge/protocol.md) and
[CLI instructions](../../bridge/cli.md). The calling/main agent must provide the
broader product/technical goal, motivations, constraints, decision rationale, and
intended outcome, including intended user impact. A task ticket or code snippet alone
is insufficient. Confirm that implementation is within the user's existing request. Never set
`subagents`: the runner refuses it for implementation.

1. Prepare a concrete specification: required behavior, inputs and outputs, edge
   cases, compatibility, error handling, and testable acceptance criteria. Explain
   the rationale for key decisions and identify choices the delegate can make.
2. Specify the workspace, exact write paths, read paths, excluded files, and expected
   patch/handoff. Record the starting commit and dirty/untracked state. Preserve user
   work. Prefer a dedicated checkout for overlapping work; include relevant uncommitted
   inputs explicitly because a new worktree starts from committed state. Never edit
   the same files concurrently with the delegate.
3. Include project instructions, relevant architecture, conventions, and exact local
   verification commands. Bound test output locations. Check those commands for
   external side effects before pre-approving them. Dependencies, remote services,
   migrations, deployment, and publishing require separate explicit authorization.
4. Dispatch the specification through the other CLI with `delegate-implement` and
   nonempty `write_paths`. The delegate can edit scoped code and run proportionate
   verification. If requirements conflict or edits must exceed scope, stop and return
   the concrete blocker. Do not recursively delegate, widen scope, or commit by default.
5. Require a concise JSON handoff: changed paths and why, acceptance criteria results,
   exact tests run and outcomes, tests not run and why, remaining concerns, and any
   deviation from the specification. Include failed checks; "not run" is not "passed".
6. Inspect the actual diff, including untracked files, and compare it against the
   baseline and write scope. Reconcile partial work after errors. Run only checks
   needed to resolve gaps or validate integration. Do not claim success based solely
   on the delegate's summary. Integrate a separate checkout only after reviewing its
   changes, preserving unrelated work.
7. **Fix turns.** If the diff misses criteria, resume with the same `--session-file`
   and send the failing criteria or review notes, within the same scope. Start a fix
   turn only after you read the diff, never automatically after a failure or timeout.
   A read-only session never becomes an implementation session; use a new session file.

Use `responses/delegate-implement.schema.json`. Each acceptance criterion has a
result (`met`, `not_met`, or `not_verified`) and evidence. Each test records its command,
result (`passed`, `failed`, or `not_run`), and details. A `complete` transport response
does not mean every criterion passed: the main agent must inspect these fields and
the actual work before declaring the implementation complete.
