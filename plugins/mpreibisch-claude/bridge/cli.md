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
  --session-file "$HANDOFF/session.json" \
  --output-dir "$HANDOFF/call-0"
```

`--output-dir` must not exist. The caller creates only its parent scratch directory.
Use `--timeout SECONDS` to change the default 3600-second model-call timeout. Model and effort
defaults come from [models.json](models.json); user choices override them.
Use `--dry-run` to validate and write `command.json` without invoking a model.
`MAX_ROUNDS` belongs in the handoff's `exchange.max_rounds`, not this timeout.

The helper passes the full request through stdin and uses argument arrays, not shell
interpolation. An exit code of zero means the response passed the schema and the peer
reported `complete`. A nonzero exit means the main agent must inspect the response or
`failure.json`.

## Sessions and recovery

`--session-file` names the task's peer session record. If the file does not exist, the
call starts a new session and writes `{target, session_id, model, effort}` to it. If it
exists, the call resumes that session with the saved model and effort. An explicit
`--model` or `--effort` replaces the saved value for that call and all later ones; an
effort-only override keeps the saved model. The session file must be outside the
workspace. Without `--session-file`, the call starts a new session recorded in
`OUTPUT_DIR/session.json`, which a later call can pass to resume it. A corrupt record or
a failed resume is reported, never replaced silently. Every new and resumed call is
built from the same flag list, so all permission flags repeat on every resume.

The runner records the session after every call that started, including a timeout or
an interruption, and prints `Peer session: PATH` on stderr. To recover a stopped call:

1. Confirm that the old process stopped, and read `failure.json`, `stdout.txt`, and
   `stderr.txt`.
2. For implementation, inspect and reconcile partial edits first.
3. Resume with the same `--session-file` and a request that asks for the final answer.

If the runner itself died before it wrote the record, take the Codex ID from the
`thread.started` event in the saved `stdout.txt`; a missing record does not prove that
no session started. If no ID exists, the call cannot be resumed: say so. Never start a
replacement session silently, and never replay an implementation automatically.

## Models and effort

These defaults apply to the receiving CLI, not to the calling agent's model:

| Workflow | Claude Code target | Codex target |
| --- | --- | --- |
| Consensus, adversarial review, exploration, brainstorm | `claude-opus-5-5`, `xhigh` | `gpt-6-astra`, `xhigh` |
| Implementation | `claude-opus-5-5`, `xhigh` | `gpt-6-astra`, `xhigh` |

Respect any model or effort the user names. Pass the choices explicitly:

```sh
python3 "$PLUGIN_ROOT/scripts/cross_model.py" \
  --request "$HANDOFF/request.json" --output-dir "$HANDOFF/custom-call" \
  --model "$MODEL_ID" --effort "$EFFORT"
```

The helper accepts any model ID or alias supported by the target CLI and account.
There is no model whitelist. With `--model` alone, it omits effort so the chosen model
can use its own default. With `--effort` alone, a new session uses the workflow's default
model, and a resumed session keeps its saved model.
Use `--effort default` to omit the effort setting even with a default model. Explicit
effort values pass through unchanged; the target CLI validates compatibility.
Claude receives `--effort LEVEL`; Codex receives `-c model_reasoning_effort="LEVEL"`.
The final arguments are saved in `command.json`, including defaults and overrides.

A resumed session keeps its model and effort unless the user changes them. Record an
authorized change in the decision artifact. Do not silently substitute another model
after availability or authentication errors. `clear-writing` runs in the calling host
and does not start another model.

Effort flags follow the [Claude CLI reference](https://code.claude.com/docs/en/cli-reference)
and the [Codex configuration reference](https://developers.openai.com/codex/config-reference).

## Sub-agents

By default the receiver works alone. To let it spawn read-only sub-agents of its own
model family, add `subagents` to the request with a `model` and an optional `effort`.
Only `delegate-explore`, `brainstorm`, `consensus`, and `adversarial-review` accept it;
`delegate-implement` refuses it. Set it only when the user asks for receiver
sub-agents. Without `effort`, the sub-agent model uses its own default.

Claude asks Codex (Astra xhigh, sub-agents Terra 6.1 high): run with `--model gpt-6-astra
--effort xhigh` and put this in the request:

```json
"subagents": {"model": "gpt-6.1-terra", "effort": "high"}
```

Codex asks Claude (Opus 5.5 high, sub-agents Sonnet 5.5 high): run with `--model
claude-opus-5-5 --effort high` and put this in the request:

```json
"subagents": {"model": "claude-sonnet-5-5", "effort": "high"}
```

- Codex target: the runner drops the multi-agent disable flags and sets
  `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort`.
  Spawned agents inherit the read-only sandbox and the `never` approval policy
  ([subagents](https://developers.openai.com/codex/subagents)).
- Claude target: the runner adds `Agent` to `--tools` and `--allowedTools` and defines
  one `reader` agent through `--agents` with `Read`, `Glob`, `Grep`, the model, and the
  effort ([sub-agents](https://code.claude.com/docs/en/sub-agents)). Every sub-agent,
  including built-in types, gets at most the parent's `Read`, `Glob`, `Grep`, and
  `Agent` tools.

The receiver prompt asks it to keep the configured model and effort. Both CLIs let a
spawn call override them, so this is an instruction, not a guarantee. Changing
`subagents` on a resumed session is allowed: it stays read-only either way.

## Claude Code target

Read-only calls expose only `Read`, `Glob`, and `Grep` (plus `Agent` with `subagents`),
with `dontAsk` permissions.
Implementation calls add `Edit`, `Write`, and `Bash`; only the listed verification
commands are pre-approved for Bash. Automatic hooks are disabled and configured MCP
servers are excluded. Restricted mode confines file tools to the workspace. Local
settings are excluded so unrelated tool grants do not widen the lane. Managed policy
still applies. The request supplies relevant project conventions and instructions.

The helper uses `--output-format json --json-schema ...` and extracts
`structured_output`. It rejects CLI errors even if the process exit code is zero.
A new call passes a runner-generated UUID with `--session-id`; a resumed call passes
`--resume UUID`.
Before dispatch, `claude auth status` checks authentication with a 30-second timeout.
Only its exit status is used. Auth stdout and stderr are discarded so account details
and credentials never enter the runner's logs. A failed or unavailable check stops
the lane before a model call. `preflight.json` records a successful check; dry runs
skip the check. This verifies CLI authentication status, not model access or remaining
quota. Model dispatch can still fail after a successful check.

The auth command and its exit-status contract are described in the
[Claude CLI reference](https://code.claude.com/docs/en/cli-reference#cli-commands).
The check adds no dependencies or model requests.

It does not use `--bare`, which skips normal OAuth and keychain authentication. If a command is denied, report it; do not grant broad
`Bash(*)` access to make the call finish.

## Codex target

Calls use `codex exec` (new) or `codex exec resume ID` (resumed), approval policy
`never`, and `read-only` sandboxing. Implementation alone switches to `workspace-write`.
`exec resume` has no sandbox flag, so `--ask-for-approval` and `--sandbox` go before
`exec` in both shapes. Network access stays disabled; web search, apps, plugins, and
hooks are disabled. Without `subagents`, the runner also passes the multi-agent disable
flags, but some models keep their agent tools, so the no-spawn rule is enforced through
instructions (see Known limits). `--disable apps` matters most: the
sandbox covers shell commands only, and without it a read-only session still exposes
connected app tools that can write. User configuration is excluded, including inherited
MCP servers. Authentication still uses the normal Codex credentials. Project
instructions remain applicable.

The helper uses `--output-schema` and `--json`. It reads the session ID from the
`thread.started` event. After a successful exit and a `turn.completed` event, it takes
the response from the last completed `agent_message` item. Timeout and interruption
never turn an earlier message into a response. It does not use `--output-last-message`
(see Known limits). It disables inherited shell execution
rules so old allow rules cannot widen the sandbox. Workflow defaults remain overridable
without changing permissions.

## Progress and failure handling

The runner prints a start message and checks saved output every 30 seconds until
completion or the configured timeout. Each check reports elapsed time and whether
output changed. It overwrites `progress.json` with elapsed time, output byte counts,
and time since the last observed output change. It does not echo output contents.
Claude's JSON transport can stay quiet until completion. Silence alone does not
establish that a process is hung; output activity alone does not prove useful work.

`stdout.txt` and `stderr.txt` remain available after failure. Every failure of a call
that created its output directory leaves `failure.json` with a reason and, when one
exists, the session file. Timeout and interruption have distinct reasons and preserve
the final progress sample. Authentication failures have separate preflight reasons.
Inspect these private local artifacts before deciding whether another call is needed.
Never treat a partial response as a completed review or retry automatically; resume the
session deliberately, as described in Sessions and recovery.

The runner supplies the complete UTF-8 prompt through a secure, seekable
`TemporaryFile` as stdin. The context manager closes and deletes it after the child
exits or the call fails. Progress checks use `Popen.wait` with a monotonic deadline;
they do not interrupt prompt delivery. Stdout and stderr go directly to diagnostic
files, so no pipe writer or output-draining thread is required. See the
[Python temporary-file documentation](https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryFile)
and [subprocess wait documentation](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait).

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

## Known limits

- Codex's model catalog sets the multi-agent version per model. On models such as
  `gpt-6-astra`, `--disable multi_agent` and `--disable multi_agent_v2` don't remove the
  agent tools; the session only spawns agents when explicitly asked. Without
  `subagents`, the receiver prompt forbids that. Shell access could reach the other CLI
  either way, so the no-recursive-delegation rule is an instruction, not a guarantee.
- `--output-last-message` can exit without writing its file on resume, so the runner
  reads the final answer from the `--json` events.
