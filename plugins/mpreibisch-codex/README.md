# Mpreibisch skills for Codex

Codex calls Claude Code for consensus, adversarial review, exploration, and scoped
implementation. `clear-writing` provides the same writing rules as the Claude package.

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

## Models

Claude defaults to Opus 5 (`claude-opus-5`) at high effort for consensus, review, and
exploration. Implementation uses Opus 5 at low effort. These settings affect the
receiving Claude process, not your Codex session.

Ask for any model supported by your Claude CLI and account. The helper accepts
`--model MODEL_ID --effort LEVEL`. With `--model` alone, effort uses the model's own
default; `--effort` alone keeps the workflow's model. Use `--effort default` to omit
the effort setting. See [model settings and examples](bridge/cli.md#models-and-effort).

## Examples

Invoke the skills in Codex:

```text
$consensus Assess this cache design with Claude. Our goal is lower checkout latency;
we chose bounded staleness to protect inventory accuracy. Compare against those
constraints and return a shared conclusion or a split decision. MAX_ROUNDS=3.

$adversarial-review Ask Claude to challenge this diff for retry and timeout failures.
Use the checkout goal and API compatibility constraints from this conversation.

$delegate-explore Have Claude trace request IDs in src/checkout and tests/checkout.
We need to choose an idempotency boundary. Return a call-path map with evidence.

$delegate-implement Have Claude implement the agreed validation change in src/input
and tests/input. Preserve the public API and meet the acceptance criteria above.

$clear-writing Rewrite this README for clarity while preserving its meaning.
```

The main agent fills the required context from the conversation before calling
Claude. See [the handoff protocol](bridge/protocol.md),
[request template](bridge/request.example.json), and [CLI guide](bridge/cli.md).
Read-only skills expose only Claude's file-reading tools. Implementation adds scoped
edits and explicitly listed verification commands. No remote actions are enabled.

For maintenance or offline checks, use the validation instructions in the repository
README. The imported writing references, output style, and optional hook script are
preserved inside `skills/clear-writing`; no global hook is registered.
