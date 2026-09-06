# Run the other agent

Resolve the plugin root from the loaded `SKILL.md` path: it is two directories above
the skill directory. All referenced resources ship inside that root. In Claude Code,
`${CLAUDE_PLUGIN_ROOT}` also identifies the installed plugin. Do not use the source
repository path after installation.

Use Python 3.10+ and the target CLI on `PATH`. Run `claude auth login` and `codex login`
interactively before delegation if those CLIs need authentication. Never put tokens
in the handoff. The runner reads `host.json`: Codex calls `claude`; Claude Code calls
`codex`. It does not invoke its calling host again.

From the calling agent, resolve the following absolute paths and run:

```sh
python3 "$PLUGIN_ROOT/scripts/cross_model.py" \
  --request "$HANDOFF/request.json" \
  --output-dir "$HANDOFF/call-0"
```

`--output-dir` must not exist. The caller creates only its parent scratch directory.
Set `--timeout 600` to change the default ten-minute timeout. Model and effort
defaults come from [models.json](models.json); user choices override them.
Use `--dry-run` to validate and write `command.json` without invoking a model.
`MAX_ROUNDS` belongs in the handoff's `exchange.max_rounds`, not this timeout.

The helper starts a fresh session for each call, passing the full request through
stdin. It uses argument arrays, not shell interpolation. An exit code of zero means
the response passed the schema and the peer reported `complete`. A nonzero exit
means the main agent must inspect the response or failure diagnostics.

## Models and effort

These defaults apply to the receiving CLI, not to the calling agent's model:

| Workflow | Claude Code target | Codex target |
| --- | --- | --- |
| Consensus, adversarial review, exploration | `claude-opus-5`, `high` | `gpt-5.6-terra`, `high` |
| Implementation | `claude-opus-5`, `low` | `gpt-5.6-luna`, `xhigh` |

Respect any model or effort the user names. Pass the choices explicitly:

```sh
python3 "$PLUGIN_ROOT/scripts/cross_model.py" \
  --request "$HANDOFF/request.json" --output-dir "$HANDOFF/custom-call" \
  --model "$MODEL_ID" --effort "$EFFORT"
```

The helper accepts any model ID or alias supported by the target CLI and account.
There is no model whitelist. With `--model` alone, it omits effort so the chosen model
can use its own default. With `--effort` alone, it keeps the workflow's default model.
Use `--effort default` to omit the effort setting even with a default model. Explicit
effort values pass through unchanged; the target CLI validates compatibility.
Claude receives `--effort LEVEL`; Codex receives `-c model_reasoning_effort="LEVEL"`.
The final arguments are saved in `command.json`, including defaults and overrides.

Keep the same selected peer model and effort throughout one consensus run unless
the user changes them. Record an authorized change in the decision artifact. Do not
silently substitute another model after availability or authentication errors.
`clear-writing` runs in the calling host and does not start another model.

Model IDs and effort controls were checked against the official
[Opus 5 documentation](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5),
[Terra documentation](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
[Luna documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Claude CLI reference](https://code.claude.com/docs/en/cli-reference), and
[Codex configuration reference](https://developers.openai.com/codex/config-reference).

## Claude Code target

Read-only calls expose only `Read`, `Glob`, and `Grep`, with `dontAsk` permissions.
Implementation calls add `Edit`, `Write`, and `Bash`; only the listed verification
commands are pre-approved for Bash. Automatic hooks are disabled and configured MCP
servers are excluded. Restricted mode confines file tools to the workspace. Local
settings are excluded so unrelated tool grants do not widen the lane. Managed policy
still applies. The request supplies relevant project conventions and instructions.

The helper uses `--output-format json --json-schema ...` and extracts
`structured_output`. It rejects CLI errors even if the process exit code is zero.
It does not use `--bare`, which skips normal OAuth/keychain authentication on the
tested Claude Code version. If a command is denied, report it; do not grant broad
`Bash(*)` access to make the call finish.

## Codex target

Calls use `codex exec`, approval policy `never`, and `read-only` sandboxing.
Implementation alone switches to `workspace-write`. Network access stays disabled;
web search, apps, plugins, hooks, and further agent delegation are disabled. User
configuration is excluded, including inherited MCP servers. Authentication still
uses the normal Codex credentials. Project instructions remain applicable.

The helper uses `--output-schema` and `--output-last-message`, with an ephemeral
session. It disables inherited shell execution rules so old allow rules cannot
widen the sandbox. Workflow defaults remain overridable without changing permissions.

## Failure handling

On unsupported flags, authentication failure, denied tools, invalid JSON, timeout,
empty output, or nonzero CLI exit, stop that lane and report the concrete failure.
Do not infer model agreement or test success from diagnostics. Do not replay an
implementation automatically. If the parent process is interrupted, reconcile any
partial edits before proceeding. The helper terminates its child process group on
timeout or interruption.

CLI permission controls enforce tool/workspace limits, while exact file scope and
test intent also require agent compliance and caller review. These skills are not
an operating-system isolation system. Use a dedicated environment when that boundary
must be enforced against arbitrary code. Unsupported CLI versions fail closed.
