# Mpreibisch skills for Claude Code

Claude Code calls Codex for consensus, adversarial review, brainstorming, exploration,
and scoped implementation, keeping one Codex session per task. `clear-writing`
provides the same writing rules as the Codex package, `artifact-standards` the same
HTML page standards, and `pr-review-ask` the same PR review-request format.
`decisions` uses the OpenAI Decisions API for fixed judgments and can gate expensive agents.

## Install and authenticate

From the root of your clone of `mpreibisch-skills`, run:

```sh
claude plugin marketplace add ./
claude plugin install mpreibisch-claude@mpreibisch-skills --scope user
codex login
```

Start a new Claude Code session after installation. Install Python 3.10+ and ensure
`codex` is on `PATH` in the environment that runs Claude Code. Claude Code itself can
authenticate with `claude auth login`. Keep credentials in each CLI's normal store;
API keys and provider configuration never belong in the plugin.

The repository's `.claude-plugin/marketplace.json` uses relative plugin paths.
Register the clone's root on each machine. If you move the clone, register its new
location. The user installation scope makes the plugin available across projects.
For temporary local testing without installation, run from the repository root:

```sh
claude --plugin-dir ./plugins/mpreibisch-claude
```

Calls report output activity every 30 seconds and preserve timeout diagnostics.
Quiet output does not establish a hung process. See
[progress and failure handling](bridge/cli.md#progress-and-failure-handling).

Each task keeps one Codex session: every call passes the same `--session-file`, so
Codex keeps its context across rounds and follow-ups, and a stopped call can resume.
Codex keeps these transcripts in its normal session store. See
[sessions and recovery](bridge/cli.md#sessions-and-recovery).

## Models

Codex defaults to GPT-6 Astra (`gpt-6-astra`) at xhigh effort for every workflow.
These settings affect the receiving Codex process, not your Claude Code session.

Ask for any model supported by your Codex CLI and account. The helper accepts
`--model MODEL_ID --effort LEVEL`. With `--model` alone, effort uses the model's own
default. With `--effort` alone, a new session uses the workflow's model and a resumed
session keeps its saved model. Use `--effort default` to omit the effort setting. See
[model settings and examples](bridge/cli.md#models-and-effort).

## Decisions setup

The [decisions skill](skills/decisions/SKILL.md) also runs without a peer CLI.
Install or update this plugin, enable marketplace auto-update where supported, and start a new session.
Claude Code can use it proactively for fixed judgments in polling, triage, routing, and classification loops.

Set `OPENAI_API_KEY` through your secret store in the environment that starts Claude Code.
Alternatively, set `DECISIONS_KEY_CMD` to a command that prints only the key.
The command runs as arguments without a shell. Never paste a key into chat or files.
Claude Code login does not supply this API key.

Ask Claude Code to resolve this installed package's `skills/decisions/scripts/decide.py` and run it with `--check`.
The check makes no network call. The skill uses Python 3.10+ and `gpt-6-luna` through the API.
Calibrate with labeled examples or shadow mode before skipping LLM calls.
Every error falls back to the LLM. The skill documents gate conditions and private JSONL logs.
Use `--preset progress-watch --gate` for the supplied watcher rule.
All bundled presets, including the watcher and relevance filter, default to shadow mode until locally evaluated and enforced.
Overridden preset rules default to shadow even when the source is calibrated; `--enforce` opts in after local evaluation.
The [authoring guide](skills/decisions/references/authoring.md) defines evidence and fallbacks.
[External templates](skills/decisions/examples/README.md) show caller-defined request routing and severity rubrics.
Presets are optional: fixed judgments over sufficient supplied text can use custom questions.
Keep local configuration with `--preset-file PATH`; `--shadow` logs any gate while returning `RUN`.
Use `report --log FILE --labels FILE` to compare proposals with independent outcome IDs offline.
The binary report evaluates one defined skip decision, not routing labels or tier adequacy.
The skill includes deterministic checks before API calls; the caller retains loop state and scheduling.

## Examples

Invoke the namespaced skills in Claude Code:

```text
/mpreibisch-claude:consensus Assess this cache design with Codex. Our goal is lower
checkout latency; bounded staleness protects inventory accuracy. Compare against
those constraints and return a shared conclusion or a split decision. MAX_ROUNDS=3.

/mpreibisch-claude:adversarial-review Ask Codex to challenge this diff for retry and
timeout failures. Use the checkout goal and API constraints from this conversation.

/mpreibisch-claude:brainstorm Brainstorm with Codex how to cut checkout latency
without stale inventory. Rank the ideas by risk and effort, and keep any disagreement.

/mpreibisch-claude:delegate-explore Have Codex trace request IDs in src/checkout and
tests/checkout. We need an idempotency boundary. Return a call-path map with evidence.

/mpreibisch-claude:delegate-implement Have Codex implement the agreed validation change
in src/input and tests/input. Preserve the API and meet the acceptance criteria above.

/mpreibisch-claude:clear-writing Rewrite this README without changing its meaning.

/mpreibisch-claude:artifact-standards Build a shareable HTML page explaining how our
retry path works, for a teammate with no context on this service.

/mpreibisch-claude:pr-review-ask Draft a review request for #4312 and #4315 for the
platform team. They fix the retry budget; #4315 is stacked on #4312. Tag @ana on the
second one.

/mpreibisch-claude:decisions Classify these build events before the expensive watcher.
Keep the LLM running in shadow mode until the thresholds are validated.
```

The main agent fills the broader context before calling Codex. See
[the handoff protocol](bridge/protocol.md), [request template](bridge/request.example.json),
and [CLI guide](bridge/cli.md). Read-only calls use Codex's read-only sandbox.
Implementation uses workspace-write with network access disabled. The caller checks
the exact file scope and acceptance criteria before accepting the changes.

`artifact-standards` starts no cross-model call and needs no `codex` CLI. It writes
one self-contained HTML file outside every repository worktree, then publishes it with
the `Artifact` tool when your request or standing authorization permits publishing;
otherwise it hands you the local file. Its page shell and design guidance ship inside
`skills/artifact-standards`, so it works whether or not the host's own artifact design
skills are loaded.

`pr-review-ask` needs an authenticated `gh`. It shows the draft in chat. If you name a
destination and Claude Code has a draft tool for it, the skill saves the draft there;
otherwise it hands you paste-ready text. It never sends; you send it yourself.

The writing references, output style, and optional hook script remain under
`skills/clear-writing`. They are preserved without activating global hooks or styles.
The skill itself supplies the writing instructions. Use `claude plugin validate`
against this directory to validate the Claude manifest and skills.
