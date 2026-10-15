# Voice reference

Invented examples of the register. Copy the register, not the sentences. Names,
projects, and numbers are placeholders.

## Channel post, three independent PRs, one focused ask

```
Hey team, uploads over 50 MB fail about one time in twenty, and retries make it worse because they start again from zero. These three PRs make large uploads resumable and show where they fail.

- [Resume uploads from the last confirmed chunk (#812)](https://github.com/OWNER/REPO/pull/812): Retries continue from the last chunk the server confirmed instead of starting over.
- [Show upload failure reasons on the status page (#815)](https://github.com/OWNER/REPO/pull/815): Separates timeouts from rejected files, so network trouble and bad input no longer look the same.
- [Document chunk size limits (#816)](https://github.com/OWNER/REPO/pull/816): Docs only.

@reviewer-a, could you look closely at the retry logic in #812? It changes behavior for every client.

Could you please review these?
```

## Message to one person, one stack that lands in order

```
Hi Sam, the config loader rewrite is ready, in three PRs that land in order:

- [Parse config files into typed settings (#430)](https://github.com/OWNER/REPO/pull/430): Replaces the string map with typed fields and clear errors for unknown keys.
  - [Read settings from environment variables (#431)](https://github.com/OWNER/REPO/pull/431): Environment values override file values, as we discussed. Stacked on #430.
    - [Remove the old loader (#432)](https://github.com/OWNER/REPO/pull/432): Deletes the string map and its last callers. Stacked on #431.

Existing config files behave the same. Would appreciate a look whenever you get a chance.
```

## Message to one person, one small PR

```
Hi Alex, small one: [Fix the repeated item on the last page (#977)](https://github.com/OWNER/REPO/pull/977). The last page of search results showed one item twice. Could you take a look today?
```

## What the samples have in common

- Opens with a short greeting or the person's name, then goes straight to why.
- The why is one to three sentences in plain words: what was observed, what it costs,
  what the PRs do about it.
- Each bullet is one sentence, sometimes two. It says what changes and why it matters,
  not how.
- Stack order is stated ("land in order", "stacked on"). Readers know what lands first.
- Honest scope notes: "Docs only", "Existing config files behave the same".
- The ask is short and polite without being soft.
- A targeted ask names the person and the part to look at.
- No exclamation points in the ask, no em dashes, no filler, no thanks-in-advance.
