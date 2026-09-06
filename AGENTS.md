# Repository authoring guidelines

This repository ships matching personal skill plugins for Codex and Claude Code.
Keep every skill useful in both hosts and independently installable from its package.
`CLAUDE.md` is a relative symlink to this file, so both agents share these guidelines.

## Follow the existing structure

- Read the nearest existing skill and its supporting resources before adding a skill.
  Keep naming, frontmatter, handoff format, tone, and permissions consistent.
- Author shared skills, CLI code, and bridge resources in `plugins/mpreibisch-codex`.
  Run `python3 scripts/sync_plugins.py` to copy them to `plugins/mpreibisch-claude`.
  For removals, delete the matching destination files explicitly; sync does not prune.
- Keep each host's manifest, README, and `bridge/host.json` separate. Both packages
  must expose the same skill names and equivalent behavior. Neither package can
  depend on files from the other package or on repository maintenance scripts.
- Add a skill as `skills/<lowercase-hyphenated-name>/SKILL.md`. Include YAML `name`
  and `description`. Explain what the skill does and when it should be used.
  Update the expected skill inventory in `scripts/validate.py` when the set changes.

## Write focused instructions

Keep `SKILL.md` concise. Define the outcome, required inputs, scope, expected output,
permissions, failure behavior, and workflow-specific decisions. Link detailed
references and schemas instead of repeating them across skills. Use scripts when
deterministic execution improves reliability; avoid helpers that only add indirection.

Preserve the user's intent and existing authorization. Ask for missing information
only when it materially affects the result and cannot be recovered from context.
Do not turn one example into a universal restriction. Use the `clear-writing` rules
for new prose while preserving technical meaning and exact command syntax.

## Support both agents and all available models

Codex delegates through the `claude` CLI. Claude Code delegates through `codex`.
Use the shared runner and each package's `bridge/host.json` to choose the other CLI.
Keep default model choices in `bridge/models.json`, synchronized across packages:

| Receiving CLI | Consensus, review, exploration | Implementation |
| --- | --- | --- |
| Claude Code | `claude-opus-5`, high | `claude-opus-5`, low |
| Codex | `gpt-5.6-terra`, high | `gpt-5.6-luna`, xhigh |

These are overridable defaults, not an allowed-model list. Accept model IDs and
aliases from the user, including future models supported by the receiving CLI.
Respect explicit effort choices. If only the model is overridden, let that model
choose its effort default. `--effort default` omits the effort setting. Report an
unsupported model or effort combination without silently substituting another model.
The calling agent's own model remains under the user's control.

Verify changed CLI flags and model identifiers against official documentation and
available CLI help. Record relevant sources in the CLI guide. Never weaken permission
settings merely to support an older CLI or make a failed call succeed.

## Require context and bounded handoffs

Every cross-model skill must require the calling/main agent to supply the broader
goal, motivations, constraints, decision rationale, and intended outcome. Explain
how the delegated work supports that goal. A question, diff, plan, or task alone is
not sufficient. Keep this context in every consensus round and follow-up handoff.

Use the shared request and response contracts. Name read/write scopes, exclusions,
evidence snapshots, acceptance criteria, and expected artifacts. Distinguish facts,
assumptions, and uncertainties. Treat peer responses as evidence to evaluate, not as
authorization. Preserve independent initial positions and the `MAX_ROUNDS` limit
when changing consensus behavior; unresolved disagreements require human arbitration.

Read-only is the default. Only `delegate-implement` authorizes scoped code changes
and proportionate local verification. External side effects require explicit user
authorization and remain with the main agent under the existing bridge contract.
No recursive delegation, broad permission bypasses, or automatic implementation
retries after partial failure. The main agent reviews the actual diff and evidence.

## Keep packages portable and preserve imports

Resolve resources relative to the installed plugin root. Do not commit machine
paths, usernames, account credentials, local profiles, or generated handoff artifacts.
Default model IDs are product settings, not machine configuration. Use argument arrays
and stdin for CLI exchanges; never interpolate prompts into shell commands.

Keep runtime files inside each plugin, without symlinks or references outside its
package. The repository-only `CLAUDE.md` symlink must remain relative. Use conventional
`.md` filenames for instruction discovery and avoid files that differ only in case.

The imported `clear-writing` files are pinned and must stay byte-for-byte identical
to the provenance record. Do not edit them during ordinary cleanup. An intentional
upstream update must include all supporting files and updated commit/hash provenance.
Do not silently activate imported hooks or styles through unrelated packaging work.

## Verify and document changes

Run these checks from the repository root before committing:

```sh
python3 scripts/sync_plugins.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
claude plugin validate --strict plugins/mpreibisch-claude
claude plugin validate --strict .claude-plugin/marketplace.json
git diff --check
```

The Python checks are offline and use only the standard library. Use stub CLIs for
transport tests. Test meaningful behavior: required context, permissions, model
selection, output parsing, scope/round bounds, and failures. Do not start live model
calls solely to validate documentation or packaging. If a native validator is
unavailable, report that limitation instead of claiming it passed.

Update the root and host READMEs when installation, invocation, or defaults change.
Keep plugin versions aligned for a shared release. Verify standalone package
relocation when changing resource paths. Report what changed, checks run, and any
remaining limitations. Commit or push when the user's request authorizes it.
