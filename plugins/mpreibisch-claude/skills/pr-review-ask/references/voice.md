# Voice reference

Real review asks the user wrote, lightly anonymized. Copy the register, not the
sentences. Names and IDs are placeholders.

## Channel post, five PRs, focused asks at the end

```
Hey folks :wave::skin-tone-2: I was investigating Groot instability and found tool call failures worth digging into. Along the way, I found a few places where error handling loses useful information or makes retries harder to classify.

Can you review these five PRs from the Groot timeout investigation? They address avoidable tool failures, cancellation gaps, and misleading dashboard metrics:

• [Grafana error handling (#43463)](https://github.com/OWNER/REPO/pull/…): Error summaries were losing the HTTP status. This preserves it so retry rules can distinguish invalid queries from temporary service failures.
• [Request deadlines and cleanup (#43465)](https://github.com/OWNER/REPO/pull/…): Stops additional HTTP attempts after a request expires or is cancelled. Cleanup gets a separate five-second window so it can finish without holding up the caller indefinitely.
    ◦ [Native tool cancellation (#43473)](https://github.com/OWNER/REPO/pull/…): Passes cancellation through native tool execution and prevents tools from starting after cancellation. Stacked on #43465.
• [Git tool instructions (#43461)](https://github.com/OWNER/REPO/pull/…): Adds examples for required arguments that agents were getting wrong. This changes instructions only.
• [Tool failure dashboard (#43462)](https://github.com/OWNER/REPO/pull/…): Separates unknown outcomes from successes and shows failures the dashboard previously hid.

<@REVIEWER_A>, <@REVIEWER_B>: can you especially focus on the cancellation behavior and compatibility with existing integrations?

<@REVIEWER_C>: can you check the training metrics in the dashboard?
```

## Channel post, three PRs, one motivation sentence

```
Could I get reviews on these three PRs? We've seen canvases time out at ~400–480 concurrent evals, with slow model calls and retries consuming substantial run time. These changes improve diagnosis and fix a cancellation gap before we increase concurrency further.

• [#43339](https://github.com/OWNER/REPO/pull/…): Show failed model-attempt latency and Fireworks separately in Groot Health, with a link to model details.
• [#43340](https://github.com/OWNER/REPO/pull/…): Add attempt/request timings, terminal status, and inspectable canvas/workflow IDs to the existing model errors table.
• [#43353](https://github.com/OWNER/REPO/pull/…): Connect activity cancellation to model requests so canceled turns can stop waiting for a response.

These reuse existing telemetry and cancellation mechanisms. We still need runtime verification before treating the canvas timeout issue as resolved, but these will help with visibility and diagnosis.

<@REVIEWER_A> <@REVIEWER_B> :pray::skin-tone-2:
```

## Group DM, one stack that lands in order

```
Hey :wave::skin-tone-2: renamed it, per your point about the plugin name. It's the Guidebook now, and everything downstream matches: CLI, MCP tools, namespace, chart.

That meant closing last week's four PRs and opening fresh ones. Same content, same order:
• [namespace + ECR repo (#43758)](https://github.com/OWNER/REPO/pull/…)
    ◦ [Helm runner access to that namespace (#43759)](https://github.com/OWNER/REPO/pull/…): second apply on purpose, same as the wiki. Stacked on #43758.
        ◦ [image build, dispatch only (#43760)](https://github.com/OWNER/REPO/pull/…): Stacked on #43759.
            ◦ [chart + corp release (#43761)](https://github.com/OWNER/REPO/pull/…): stays a draft until there's a real image tag. Stacked on #43760.

Still just another tenant on corp, nothing new on the AWS or ACL side.

Would appreciate a look whenever you get a chance :pray::skin-tone-2:
```

## DM, one small PR, one judgement call flagged

```
Hey Bill, review please: [fix(tools): rethrow the typed gateway error (#43600)](https://github.com/OWNER/REPO/pull/…)

The integrations gateway returns typed gRPC errors with a code, details and an http-status trailer. Several evidence tools caught that and threw a fresh plain Error built from the message text only. Everything downstream that decides transient vs real reads the structure, not the text, so gateway 503s were landing in the tool-error dashboard as unknown.

This is the last tool in the evidenceTasks tree with that pattern. The rest are already up as part of [RES-14302](https://linear.app/WORKSPACE/issue/RES-14302).

One judgement call worth your eye: there is an eval fixture abort branch above the throw. I kept it because it also skips the failure bookkeeping. Reasoning is in the PR body.

It's a very small PR so it would be great if you could TAL today :slightly_smiling_face:
```

## DM, two PRs, stacked

```
Hey! Could you review [#43265](https://github.com/OWNER/REPO/pull/…)?

We're preparing Groot for 1,000+ concurrent evals and need to distinguish calls waiting for a local DSS concurrency slot from calls actually running. This adds lightweight metrics for held slots, queued calls, acquisition wait and timeouts, plus panels in Groot Health. It reuses our existing telemetry without changing admission behavior. It's stacked on [#43262](https://github.com/OWNER/REPO/pull/…).
```

## DM, quick stamp

```
Hey :wave::skin-tone-2: I'm working with Emilios on cleaning up the tools area. Mind giving a stamp pls?

[#43554](https://github.com/OWNER/REPO/pull/…)
```

## What the samples have in common

- Opens with a wave or the person's name, then goes straight to why.
- The why is one to three sentences in plain words: what was observed, what it costs, what the PRs do about it.
- Each bullet is one sentence, sometimes two. It says what changes and why it matters, not how.
- Stack order is stated ("same order", "stacked on", "depends on"). Readers are told what lands first.
- Honest scope notes: "instructions only", "reuses existing telemetry", "stays a draft until".
- The ask is short and polite without being soft: "Could you please review these?", "PTAL :pray::skin-tone-2:", "would appreciate a look whenever you get a chance".
- Targeted asks name the person and the part to look at.
- No exclamation points in the ask, no em dashes, no filler, no thanks-in-advance.
