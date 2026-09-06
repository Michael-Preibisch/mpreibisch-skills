# Personal cross-model skills

Two installable plugins pair Codex and Claude Code through their CLIs. Each includes
`consensus`, `adversarial-review`, `delegate-explore`, `delegate-implement`, and the
pinned `clear-writing` skill.

| Calling host | Plugin | Receiving CLI | Installation |
| --- | --- | --- | --- |
| Codex | `mpreibisch-codex` | `claude` | [Codex README](plugins/mpreibisch-codex/README.md) |
| Claude Code | `mpreibisch-claude` | `codex` | [Claude Code README](plugins/mpreibisch-claude/README.md) |

Every cross-model request carries the broader goal, motivations, constraints,
decision rationale, intended outcome, scope, and expected output. The runner rejects
missing context fields. The main agent supplies meaningful context and verifies the
returned evidence. Only `delegate-implement` grants scoped implementation writes.
The handoff forbids external side effects, and the helper rejects requests granting
them; authorized remote actions stay with the main agent. Consensus defaults to three
exchange rounds after independent assessment.

Clone or copy this repository anywhere. Install each package on its calling host;
authenticate its receiving CLI separately. Both packages contain all their runtime
resources. No symlinks, absolute installation paths, account IDs, model names, or
credentials are embedded. Python 3.10+ is the only helper dependency.

## Validate

Run these commands from the repository root:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
claude plugin validate --strict plugins/mpreibisch-claude
claude plugin validate --strict .claude-plugin/marketplace.json
```

The Python checks need no authenticated CLI or network. They validate both manifests
against bundled schemas, package parity, skill references, and upstream file hashes.
Tests use stub CLIs to check permissions, context delivery, JSON extraction, failure
handling, and round bounds without spending model tokens. Claude's own validator
provides an additional host check when installed. The Codex package was also checked
with the official plugin-creator manifest validator during creation.

Runtime flags were checked against Codex CLI `0.151.0` and Claude Code `2.1.261`.
Other versions must support the flags in [the CLI guide](plugins/mpreibisch-codex/bridge/cli.md).
Unsupported flags fail the call; the helper never falls back to weaker permissions.
The helper includes POSIX and Windows process termination. Validation ran on macOS;
other platforms have not been integration-tested. Shell examples use POSIX syntax;
set equivalent paths in your shell. A live model call requires your own CLI
authentication and is separate from offline validation.

## Maintain

Edit common workflows, schemas, and the helper in `plugins/mpreibisch-codex`.
Run `python3 scripts/sync_plugins.py` to copy common files to the Claude package.
Keep `bridge/host.json`, manifests, and plugin READMEs host-specific. Run validation
before committing. Both installed packages work without the other package or the
repository's maintenance scripts.

The [clear-writing provenance record](provenance/clear-writing.json) records the exact
source commit and Git/SHA-256 hashes. All seven upstream files are preserved byte for
byte in each plugin. The optional output-style and Claude hook script remain bundled
at their upstream paths; installation does not register global styles or hooks.
The skill itself includes its full writing rules and references.

Packaging and CLI references:

- [OpenAI plugin documentation](https://developers.openai.com/codex/plugins)
- [OpenAI non-interactive CLI documentation](https://developers.openai.com/codex/noninteractive)
- [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code marketplace reference](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Pinned clear-writing source](https://github.com/Michael-Preibisch/second-brain/tree/f83f1c52517f58cc738b2518d9d77cfe9a22f282/plugins/second-brain/skills/clear-writing)
