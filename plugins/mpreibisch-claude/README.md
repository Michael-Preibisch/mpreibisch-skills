# Mpreibisch skills for Claude Code

Claude Code calls Codex for consensus, adversarial review, exploration, and scoped
implementation. `clear-writing` provides the same writing rules as the Codex package.

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

## Models

Codex defaults to Terra (`gpt-5.6-terra`) at high effort for consensus, review, and
exploration. Implementation uses Luna (`gpt-5.6-luna`) at xhigh effort. These settings
affect the receiving Codex process, not your Claude Code session.

Ask for any model supported by your Codex CLI and account. The helper accepts
`--model MODEL_ID --effort LEVEL`. With `--model` alone, effort uses the model's own
default; `--effort` alone keeps the workflow's model. Use `--effort default` to omit
the effort setting. See [model settings and examples](bridge/cli.md#models-and-effort).

## Examples

Invoke the namespaced skills in Claude Code:

```text
/mpreibisch-claude:consensus Assess this cache design with Codex. Our goal is lower
checkout latency; bounded staleness protects inventory accuracy. Compare against
those constraints and return a shared conclusion or a split decision. MAX_ROUNDS=3.

/mpreibisch-claude:adversarial-review Ask Codex to challenge this diff for retry and
timeout failures. Use the checkout goal and API constraints from this conversation.

/mpreibisch-claude:delegate-explore Have Codex trace request IDs in src/checkout and
tests/checkout. We need an idempotency boundary. Return a call-path map with evidence.

/mpreibisch-claude:delegate-implement Have Codex implement the agreed validation change
in src/input and tests/input. Preserve the API and meet the acceptance criteria above.

/mpreibisch-claude:clear-writing Rewrite this README without changing its meaning.
```

The main agent fills the broader context before calling Codex. See
[the handoff protocol](bridge/protocol.md), [request template](bridge/request.example.json),
and [CLI guide](bridge/cli.md). Read-only calls use Codex's read-only sandbox.
Implementation uses workspace-write with network access disabled. The caller checks
the exact file scope and acceptance criteria before accepting the changes.

The writing references, output style, and optional hook script remain under
`skills/clear-writing`. They are preserved without activating global hooks or styles.
The skill itself supplies the writing instructions. Use `claude plugin validate`
against this directory to validate the Claude manifest and skills.
