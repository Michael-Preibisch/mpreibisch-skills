# Personal cross-model skills

Two installable plugins pair Codex and Claude Code through their CLIs. Each includes
`consensus`, `adversarial-review`, `brainstorm`, `delegate-explore`, `delegate-implement`,
the pinned `clear-writing` skill, `artifact-standards`, and `pr-review-ask`.

| Calling host | Plugin | Receiving CLI | Installation |
| --- | --- | --- | --- |
| Codex | `mpreibisch-codex` | `claude` | [Codex README](plugins/mpreibisch-codex/README.md) |
| Claude Code | `mpreibisch-claude` | `codex` | [Claude Code README](plugins/mpreibisch-claude/README.md) |

`pr-review-ask` drafts a request to review one or more GitHub PRs in the user's own
voice: motivation first, one line per PR, confirmed stacks kept visible, linked issues
from GitHub. It fetches PR facts with `gh` and shows the draft in chat. If the user
names a destination and the host has a draft tool for it, it saves a draft there. It
never sends.

`brainstorm` asks the other model for ideas without showing it yours, then swaps the
lists so each side builds on and challenges the other's, and returns a ranked shortlist
that keeps the dissent. It never forces agreement; `consensus` does that.

`artifact-standards` starts no cross-model call. It holds the
house standards for every shareable HTML page: page shape, palette, a light-first
theme contract with an in-page toggle, the writing gates, terms-first for explainers,
source links, and a pre-publish checklist. It ships a page shell and design guidance
inside the skill, so it needs no host design skill. Delivery adapts to the host: the
agent always writes one self-contained HTML file outside every repository worktree,
then publishes it if the host has a publisher and the user authorized publishing, or
hands back the local file if it does not.

Every cross-model request carries the broader goal, motivations, constraints,
decision rationale, intended outcome, scope, and expected output. The runner rejects
missing context fields. The main agent supplies meaningful context and verifies the
returned evidence. Only `delegate-implement` grants scoped implementation writes.
The handoff forbids external side effects, and the helper rejects requests granting
them; authorized remote actions stay with the main agent. Consensus defaults to three
exchange rounds after independent assessment.

Each task keeps one peer session, in both directions. The caller passes the same
`--session-file` on every call: the first call starts the session, and later calls
resume it, so the other model keeps its context across consensus rounds, review
rebuttals, re-reviews, and follow-ups. Every resumed call repeats all permission flags.
See [sessions and recovery](plugins/mpreibisch-codex/bridge/cli.md#sessions-and-recovery).

Clone or copy this repository anywhere. Install each package on its calling host;
authenticate its receiving CLI separately. Both packages contain all their runtime
resources, with no machine-specific paths, profiles, account IDs, or credentials.
Python 3.10+ is the only helper dependency. Claude calls first check authentication
without retaining account details or starting a model. Both adapters report bounded
progress, preserve partial diagnostics on timeout, and keep the session so a stopped
call can resume. See the
[progress and failure guide](plugins/mpreibisch-codex/bridge/cli.md#progress-and-failure-handling).

## Repository contents

| Path | Contents |
| --- | --- |
| `plugins/mpreibisch-codex/` | Codex plugin, eight skills, shared bridge, and Claude CLI adapter |
| `plugins/mpreibisch-claude/` | Claude Code plugin, matching skills, shared bridge, and Codex CLI adapter |
| `.agents/plugins/marketplace.json` | Codex marketplace manifest |
| `.claude-plugin/marketplace.json` | Claude Code marketplace manifest |
| `provenance/` | Pinned source and hashes for `clear-writing` |
| `schemas/`, `scripts/`, `tests/` | Offline validation, package synchronization, and stub CLI tests |
| [AGENTS.md](AGENTS.md) | Skill authoring guidelines for both agents |
| `CLAUDE.md` | Relative symlink to `AGENTS.md` |

## Install

Install [Codex CLI](https://developers.openai.com/codex/cli),
[Claude Code](https://code.claude.com/docs/en/setup), and Python 3.10+.
Both CLIs must be on `PATH` in the environment running the calling agent. Authenticate
each CLI using your own account; credentials remain outside the repository.

```sh
git clone https://github.com/Michael-Preibisch/mpreibisch-skills.git
cd mpreibisch-skills
codex login
claude auth login
```

Install the Codex plugin from the clone's root:

```sh
codex plugin marketplace add .
codex plugin add mpreibisch-codex@mpreibisch-skills
```

Install the Claude Code plugin from the same directory:

```sh
claude plugin marketplace add ./
claude plugin install mpreibisch-claude@mpreibisch-skills --scope user
```

Start a new session in each host. In Codex, invoke `$consensus`, `$adversarial-review`,
`$brainstorm`, `$delegate-explore`, `$delegate-implement`, `$clear-writing`,
`$artifact-standards`, or `$pr-review-ask`.
In Claude Code, use `/mpreibisch-claude:consensus` and the corresponding namespaced
skill names.
The host READMEs above include examples. Repeat installation on each machine;
relative marketplace paths let the clone live anywhere. A private repository requires
GitHub access to clone. Installing a plugin does not authenticate the receiving CLI.

## Default models

The defaults apply to the receiving agent in each cross-model call:

| Workflow | Claude Code target | Codex target |
| --- | --- | --- |
| Consensus, adversarial review, brainstorm, exploration | Opus 5.5 (`claude-opus-5-5`), xhigh | GPT-6 Astra (`gpt-6-astra`), xhigh |
| Implementation | Opus 5.5 (`claude-opus-5-5`), xhigh | GPT-6 Astra (`gpt-6-astra`), xhigh |

All models and aliases supported by the receiving CLI and your account remain
available. `artifact-standards` and `pr-review-ask` use the calling agent's model and
start no call.
Ask the calling agent to use a specific model and effort, or pass
`--model MODEL_ID --effort LEVEL` to the helper. With only `--model`, the helper omits
effort so the selected model can use its own default. With only `--effort`, a new
session uses the workflow's default model and a resumed session keeps its saved model.
`--effort default` also omits the effort setting. A resumed session keeps its saved
model and effort unless you override them.

Defaults live in [models.json](plugins/mpreibisch-codex/bridge/models.json).
The [CLI guide](plugins/mpreibisch-codex/bridge/cli.md#models-and-effort) documents the
flags and official model references. The helper does not whitelist models or silently
substitute unavailable ones. `clear-writing` uses the calling agent's model.

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
The delegation-context rule applies only to the five cross-model skills; `clear-writing`,
`artifact-standards`, and `pr-review-ask` are exempt because they start no handoff.
Tests use stub CLIs to check permissions, session resume, context delivery, JSON
extraction, failure handling, and round bounds without spending model tokens. Claude's own validator
provides an additional host check when installed. The Codex package was also checked
with the official plugin-creator manifest validator during creation.

Runtime flags were checked against Codex CLI `0.161.0` and Claude Code `2.1.280`.
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

Follow [AGENTS.md](AGENTS.md) when creating or changing skills. `CLAUDE.md` points to
the same instructions. Preserve that relative symlink when cloning on systems where
Git symlink checkout needs explicit support. Plugin packages themselves contain no
symlinks and remain independent of this repository-only instruction link.

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
