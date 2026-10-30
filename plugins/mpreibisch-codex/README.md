# Mpreibisch skills for Codex

Codex calls Claude Code for consensus, adversarial review, brainstorming, exploration,
and scoped implementation, keeping one Claude session per task. `clear-writing`
provides the same writing rules as the Claude package, `artifact-standards` the same
HTML page standards, and `pr-review-ask` the same PR review-request format.
`decisions` uses the OpenAI Decisions API for fixed judgments and can gate expensive agents.

## Install and authenticate

From the root of your clone of `mpreibisch-skills`, run:

```sh
codex plugin marketplace add .
codex plugin add mpreibisch-codex@mpreibisch-skills
claude auth login
```

Start a new Codex session after installation. Install Python 3.10+ and ensure `claude`
is on `PATH` in the environment that runs Codex. Codex itself can authenticate with
`codex login`. CLI credentials stay in each CLI's normal credential store. If you
already use an API key or supported provider login, keep that configuration outside
the plugin. Installation does not install the CLIs.

The repository's `.agents/plugins/marketplace.json` uses relative plugin paths.
Register the clone's root on each machine. If you move the clone, register its new
location. This marketplace is named `mpreibisch-skills`; it does not depend on a
pre-existing personal marketplace. Installation copies a self-contained package.

The runner checks Claude authentication before dispatch without recording account
details. Calls report output activity every 30 seconds and preserve timeout diagnostics.
Quiet output does not establish a hung process. See
[progress and failure handling](bridge/cli.md#progress-and-failure-handling).

Each task keeps one Claude session: every call passes the same `--session-file`, so
Claude keeps its context across rounds and follow-ups, and a stopped call can resume.
Claude keeps these transcripts in its normal session store. See
[sessions and recovery](bridge/cli.md#sessions-and-recovery).

## Models

Claude defaults to Opus 5.5 (`claude-opus-5-5`) at xhigh effort for every workflow.
These settings affect the receiving Claude process, not your Codex session.

Ask for any model supported by your Claude CLI and account. The helper accepts
`--model MODEL_ID --effort LEVEL`. With `--model` alone, effort uses the model's own
default. With `--effort` alone, a new session uses the workflow's model and a resumed
session keeps its saved model. Use `--effort default` to omit the effort setting. See
[model settings and examples](bridge/cli.md#models-and-effort).

## Decisions setup

Install or update this plugin, enable marketplace auto-update where supported, and start a new session.
Codex can use `decisions` proactively for fixed judgments in polling, triage, routing, and classification loops.
It uses Python 3.10+ and `gpt-6-luna` through the API, without calling Claude Code.

Set `OPENAI_API_KEY` in the environment that starts Codex through your secret store.
Alternatively, set `DECISIONS_KEY_CMD` to a command that prints only the key.
The command runs as arguments without a shell. Never paste a key into chat or files.
Codex login does not supply this API key.

Ask Codex to resolve this installed package's `skills/decisions/scripts/decide.py` and run it with `--check`.
The check makes no network call. The [decisions skill](skills/decisions/SKILL.md) documents
question formats, gate conditions, and private JSONL logs. Calibrate with labeled examples
or shadow mode before skipping LLM calls. Every error falls back to the LLM.
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

Invoke the skills in Codex:

```text
$consensus Assess this cache design with Claude. Our goal is lower checkout latency;
we chose bounded staleness to protect inventory accuracy. Compare against those
constraints and return a shared conclusion or a split decision. MAX_ROUNDS=3.

$adversarial-review Ask Claude to challenge this diff for retry and timeout failures.
Use the checkout goal and API compatibility constraints from this conversation.

$brainstorm Brainstorm with Claude how to cut checkout latency without stale
inventory. Rank the ideas by risk and effort, and keep any disagreement.

$delegate-explore Have Claude trace request IDs in src/checkout and tests/checkout.
We need to choose an idempotency boundary. Return a call-path map with evidence.

$delegate-implement Have Claude implement the agreed validation change in src/input
and tests/input. Preserve the public API and meet the acceptance criteria above.

$clear-writing Rewrite this README for clarity while preserving its meaning.

$artifact-standards Build a shareable HTML page explaining how our retry path works,
for a teammate with no context on this service.

$pr-review-ask Draft a review request for #4312 and #4315 for the platform team.
They fix the retry budget; #4315 is stacked on #4312. Tag @ana on the second one.

$decisions Classify these build events before running the expensive watcher.
Keep the LLM running in shadow mode until the thresholds are validated.
```

The main agent fills the required context from the conversation before calling
Claude. See [the handoff protocol](bridge/protocol.md),
[request template](bridge/request.example.json), and [CLI guide](bridge/cli.md).
Read-only skills expose only Claude's file-reading tools. Implementation adds scoped
edits and explicitly listed verification commands. No remote actions are enabled.

`artifact-standards` starts no cross-model call and needs no `claude` CLI. It writes
one self-contained HTML file outside every repository worktree and hands you the file,
because Codex has no page publisher. It never starts a preview server or installs one.
Its page shell and design guidance ship inside `skills/artifact-standards`, so it does
not depend on any host design skill.

`pr-review-ask` needs an authenticated `gh`. It shows the draft in chat. If you name a
destination and Codex has a draft tool for it, for example through an MCP server you
added, the skill saves the draft there; otherwise it hands you paste-ready text. It
never sends.

For maintenance or offline checks, use the validation instructions in the repository
README. The imported writing references, output style, and optional hook script are
preserved inside `skills/clear-writing`; no global hook is registered.
