---
name: pr-review-ask
description: Draft a Slack message that asks teammates to review one or more GitHub PRs, in the user's own voice, then show it in chat and save it as a Slack draft when a Slack tool is available. Use when the user says "ask for a review", "post these PRs", "draft the review ask", "PRs are ready for review", or names PRs and a channel or person. Preserves PR stacks in the list, links Linear issues, and tags reviewers only when asked.
---

# PR review ask

One message: a wave, a few plain sentences on what the PRs do and why, a list of PRs
with one-line explainers that keeps stack structure visible, and a short ask. Written
as the user writes, see [voice](references/voice.md). Read [clear-writing](../clear-writing/SKILL.md)
first. Resolve both paths from the installed skill directory.

## Inputs

- **PRs.** From the request (URLs, `#123`, `123`, `owner/repo#123`) or from the session
  when the user says "these PRs" and the conversation already names them. Never invent
  or add PRs. If none are known, ask.
- **Destination.** A channel or person. Take it from the request or the session. If it
  is still missing, ask once, after the draft is shown.
- **Reviewers to tag.** Only the people the user names, or the PR's requested reviewers
  when the user asks to tag them. Nobody else.
- **Context the user gives.** Motivation, ticket, what to focus on. Use it; it beats
  what the PR body says.

## Gather

Run [collect_prs.py](scripts/collect_prs.py) with every PR reference. It needs an
authenticated `gh`. It returns titles, URLs, base and head branches, draft state,
requested reviewers, Linear keys, and a forest of stacks: a PR whose base branch is
another listed PR's head branch nests under it. Read each PR body for the what and
why. Read the diff only when the body does not explain the change.

Report PRs the script could not fetch and continue with the rest. A draft PR stays in
the list, marked as a draft, unless the user drops it.

## Message shape

```
Hey :wave::skin-tone-2: <one to four sentences: what these changes do and why, for a reader with some context but not deep context>

<list of PRs>

<ask>
```

**Intro.** Lead with the motivation, then the what. Simple words, no internals. Link
the Linear issue when the work has one: `[RES-1234](https://linear.app/<workspace>/issue/RES-1234)`.
Take the workspace from a Linear link in a PR body or the recent git log; if none
exists, ask. Mention it once, in the intro, not on every bullet.

**List.** One bullet per PR. Link text is the full PR title as shown on GitHub, then
the number:

```
• [<full PR title> (#123)](https://github.com/OWNER/REPO/pull/123): <one sentence, rarely two: what it changes and why>.
```

Stacks keep their shape. A child PR is indented under its parent and says what it is
stacked on:

```
• [Parent title (#101)](https://github.com/OWNER/REPO/pull/…): explainer.
    ◦ [Child title (#102)](https://github.com/OWNER/REPO/pull/…): explainer. Stacked on #101.
        ◦ [Grandchild title (#103)](https://github.com/OWNER/REPO/pull/…): explainer. Stacked on #102.
• [Independent title (#104)](https://github.com/OWNER/REPO/pull/…): explainer.
```

Use the literal `•` and `◦` characters with four-space indents; they render the same
in Slack and in chat. With more than one stack, add one line before the list that says
so ("Two stacks, each lands bottom-up:" or similar) and separate the stacks with a
blank line. With no stacks, plain bullets, no preamble.

A reviewer tag goes at the end of the bullet it applies to: `<@U0123ABCD>`. Or one
line after the list when the ask is about the whole set, as in the voice reference.

**Ask.** One line. "Could you please review these?" is the default. A DM to one
person can be shorter. Add a real constraint when there is one: small PR, no rush,
needs to land in order, one judgement call worth their eye.

## Voice rules

- Direct. State the fact, state the ask. No cheerleading, no corporate phrasing, no
  "I hope this finds you well", no exclamation points.
- Motivation first, then what changed. Assume the reader knows the codebase but not
  this work.
- Only what is true. Say a PR is small, green, or stacked only when the data says so.
- No em dashes anywhere in the message. A colon separates a link from its explainer.
- Skin-toned emoji carry `:skin-tone-2:`. Wave to open, `:pray::skin-tone-2:` for a
  thank-you or a nudge. Nothing else unless the user asks.
- Match the register of the destination: a channel post gets a fuller intro; a DM to
  someone who already knows the work gets one sentence.
- Never mention this skill, the agent, or how the message was made.

Before delivery, run the draft through the check script from the sibling skill:

```sh
node ../clear-writing/hooks/clear-writing-check.mjs --text < draft.md
```

Fix every blocking line and re-scan for the em dash character after each edit.

## Deliver

1. **Show the draft in chat**, plainly, so the user reads it as the recipient will.
   Then list the PRs the script could not fetch, if any.
2. **Resolve the destination.** A channel by name through the host's Slack channel
   search; a person through the Slack user search, whose user ID is also the DM
   channel ID. Reviewer tags resolve the same way. An unresolved person stays a plain
   name; never guess an ID.
3. **Save the draft in Slack** with whichever Slack draft tool the host exposes. In
   Claude Code that is the Slack connector's `slack_send_message_draft`; in Codex it is
   a Slack MCP server the user added with `codex mcp add`, if one offers a draft tool.
   Pass the message in standard markdown with `<@U...>` mentions inline. Report the
   returned channel link. Sending is the user's action: never call a send tool unless
   the user says "send" for this message.
4. **Without a Slack draft tool**, hand back the text and say it is a paste-ready
   draft. Slack does not render markdown links pasted into the composer, so give the
   paste variant with the bare URL after each title. In Codex, add one line saying a
   Slack MCP server with a draft tool would let the skill save the draft directly.

If the draft tool answers `draft_already_exists`, say so and hand back the text; the
user clears the existing draft or pastes over it. If `gh` is not authenticated, stop
and say which command fixes it.

Never post, edit, or react in Slack beyond creating the one draft. Never change the
PRs.
