---
name: pr-review-ask
description: Draft a concise request to review one or more GitHub PRs, explaining why the changes matter and preserving confirmed stack relationships. Use for "ask for a review", "draft a review request", or "these PRs are ready for review". Show the draft in chat; adapt it to a destination only when requested.
---

# PR review ask

One message: a short greeting, a few plain sentences on what the PRs do and why, a
list of PRs with one-line explainers that keeps stack structure visible, and a short
ask. Written as the user writes, see [voice](references/voice.md). Read
[clear-writing](../clear-writing/SKILL.md) first. Resolve both paths from the installed
skill directory.

## Inputs

- **PRs.** From the request (URLs, `#123`, `123`, `owner/repo#123`) or from the session
  when the user says "these PRs" and the conversation already names them. Never invent
  or add PRs. If none are known, ask.
- **Destination.** Optional: a channel, group, or person the user names. Without one,
  the draft stays in chat.
- **Reviewers to tag.** Only the people the user names, or the PR's requested reviewers
  when the user asks to tag them. Nobody else.
- **Context the user gives.** Motivation, linked issue, what to focus on. Use it; it
  beats what the PR body says.

## Gather

Resolve each reference to `OWNER/REPO` and a PR number. A bare number or `#123`
belongs to the current directory's repository (`gh repo view --json nameWithOwner`).
Skip duplicates. For each PR, run:

```sh
gh pr view NUMBER --repo OWNER/REPO --json number,title,url,body,state,baseRefName,headRefName,headRepository,headRepositoryOwner,isDraft,reviewRequests,closingIssuesReferences
```

This needs an authenticated `gh`. If a fetch fails, report that PR and continue with
the rest. Read each body for the what and why. Read the diff (`gh pr diff`) only when
the body does not explain the change. A draft PR stays in the list, marked as a draft,
unless the user drops it.

**Linked issues** come from `closingIssuesReferences` (the issues GitHub closes when
the PR merges), links in the PR body, or the user. Closing references are not every
related issue. Never build an issue link from a token in a title or branch name.

**Stacks.** Nest PR B under PR A only when all of these hold:

- B's `baseRefName` equals A's `headRefName`.
- A's head repository (`headRepository.nameWithOwner`) is B's repository.
- A is the only possible parent, and the chain has no cycle.

Otherwise list the PR flat and say in one short line why its order is unclear. Never
leave out a fetched PR.

## Message shape

```
Hey <name or team, optional>, <one to four sentences: what these changes do and why, for a reader with some context but not deep context>

<list of PRs>

<ask>
```

**Intro.** Lead with the motivation, then the what. Simple words, no internals. When
the work has a linked issue, link it once, in the intro, not on every bullet.

**List.** One bullet per PR. Link text is the full PR title as shown on GitHub, then
the number:

```
- [<full PR title> (#123)](https://github.com/OWNER/REPO/pull/123): <one sentence, rarely two: what it changes and why>.
```

Stacks keep their shape. A child PR is indented under its parent and says what it is
stacked on:

```
- [Parent title (#101)](https://github.com/OWNER/REPO/pull/101): explainer.
  - [Child title (#102)](https://github.com/OWNER/REPO/pull/102): explainer. Stacked on #101.
    - [Grandchild title (#103)](https://github.com/OWNER/REPO/pull/103): explainer. Stacked on #102.
- [Independent title (#104)](https://github.com/OWNER/REPO/pull/104): explainer.
```

Use plain Markdown bullets with two-space indents. With more than one stack, add one
line before the list that says so ("Two stacks, each lands bottom-up:" or similar)
and separate the stacks with a blank line. With no stacks, plain bullets, no preamble.

A reviewer tag goes at the end of the bullet it applies to, or on one line after the
list when the ask is about the whole set, as in the voice reference.

**Ask.** One line. "Could you please review these?" is the default. A message to one
person can be shorter. Add a real constraint when there is one: small PR, no rush,
needs to land in order, one judgement call worth their eye.

## Voice rules

- Direct. State the fact, state the ask. No cheerleading, no corporate phrasing, no
  "I hope this finds you well", no exclamation points.
- Motivation first, then what changed. Assume the reader knows the codebase but not
  this work.
- Only what is true. Say a PR is small, green, or stacked only when the data says so.
- No em dashes anywhere in the message. A colon separates a link from its explainer.
- Emoji only when the user's own messages or instructions use them. None by default.
- Match the register of the destination: a channel post gets a fuller intro; a message
  to someone who already knows the work gets one sentence.
- Never mention this skill, the agent, or how the message was made.

Before delivery, review the draft against the clear-writing hard bans, and search it
for the em dash character. You do this review yourself; never claim that an automated
check ran.

## Deliver

1. **Show the draft in chat**, plainly, so the user reads it as the recipient will.
   Then list the PRs that could not be fetched, if any.
2. **If the user named a destination** and the host exposes a draft tool for it, save
   the draft there by that tool's own contract. Resolve channels and people with the
   same tool's search. A person it cannot resolve stays a plain name or GitHub handle;
   never guess an ID. Use the destination's mention syntax only for identities the tool
   verified. Report where the draft was saved.
3. **Without such a tool**, hand back the text as a paste-ready draft. Some chat apps
   don't render Markdown links pasted into the composer; when that matters, also give
   a variant with the bare URL after each title.

Sending is the user's action: never call a send tool unless the user says "send" for
this message and destination. Never install or configure an integration to deliver
the draft. Never post, edit, or react anywhere beyond creating the one draft, and
never change the PRs. If `gh` is not authenticated, stop and say that `gh auth login`
fixes it.
