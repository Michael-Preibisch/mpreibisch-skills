# Plain language: anti-slop, STE, and conciseness

## Anti-slop catalog

Patterns that mark text as machine-generated filler. Remove all of them.

### Structure patterns
- **Fake-profound closer (mic drop)**: a final sentence that sounds deep and adds nothing. "And that changes everything." "The best code is the code you never write." Delete the sentence; end on the last piece of information.
- **It's-not-X-it's-Y**: "This isn't just a refactor, it's a rethinking of..." State what it is.
- **Rhetorical question + answer**: "Why does this matter? Because...". Write the statement.
- **Throat-clearing opener**: "Great question", "Let's dive in", "In the world of...", "When it comes to...". Start with the answer.
- **Recap paragraph**: a closing summary that restates the body. Delete it.
- **Signposting**: "As mentioned above", "In this section we will", "Now let's look at". Just present the content.
- **Everything-in-threes**: constant triads ("simple, fast, and reliable"). Break the rhythm; use one precise word.
- **Uniform sentence length**: all sentences 15-20 words reads as generated. Mix short and medium.
- **Over-formatting**: bold scattered for emphasis, headers on 3-line answers, nested bullets one level deep everywhere. Format only when structure needs it.
- **Empty-calorie hedging**: "might potentially", "could arguably", "in some cases it may be possible". One qualifier max, only when uncertainty is real.
- **Adjective inflation**: "powerful", "elegant", "clean", "beautiful" describing your own output or code. Facts only.
- **Both-sidesing everything**: reflexive "however, there are trade-offs" paragraphs with no specific trade-off. Name the trade-off or cut it.

### Banned words and phrases
delve, leverage (verb), robust, seamless(ly), crucial, comprehensive, holistic, landscape ("the AI landscape"), journey, elevate, streamline, empower, unlock, harness, supercharge, game-changer, cutting-edge, state-of-the-art, best-in-class, revolutionize, transformative, "it's worth noting", "it's important to note", "importantly", "notably", "in essence", "at its core", "at the end of the day", "in today's world", "ever-evolving", "dive deep", "deep dive" (as verb phrase), "a testament to", "underscores", "boasts", "myriad", "plethora", "tapestry", "navigate the complexities", "unpack".

Also banned (from the base guide): please, please note, simply, easy, just (filler), very, actually, basically, obviously, of course, as you can see.

### Punctuation tells
- **Em dash (—)**: banned outright. Replace with comma, colon, period, or parentheses. Also avoid en-dash-as-break. Hyphens in compound modifiers stay.
- **Exclamation points**: banned.
- **Ellipses for drama**: banned in prose.
- Semicolons: rare; prefer two sentences.

### Closers
- No "Let me know if...", "Hope this helps", "Happy to...", "Feel free to...".
- No emoji unless the user uses them first.
- End on content. The last sentence should carry information.

## ASD-STE100 detail

Adopted rules (adapted from the aerospace spec for general technical writing):

1. **Sentence length**: max ~20 words for procedural/instructional sentences, ~25 for descriptive. If over, split.
2. **Paragraph length**: max ~6 sentences, one topic. First sentence states the topic.
3. **One instruction per sentence.** Sequential actions get separate sentences or list items. Simultaneous actions may share a sentence ("Hold the button and turn the key").
4. **One word, one meaning.** Choose one term per concept and use it everywhere in the document. Common collision sets to standardize: delete/remove/erase; start/launch/spin up/boot; stop/end/terminate/kill (pick per context; *kill* is allowed); folder/directory; parameter/argument/flag; error/failure/fault.
5. **Approved-verb bias**: prefer the short common verb: do, make, get, set, put, use, show, start, stop, remove, add. Avoid nominalizations: "perform an installation of" -> "install"; "carry out a comparison" -> "compare"; "is responsible for the handling of" -> "handles".
6. **Noun clusters**: max 3 nouns in a row. "database connection pool exhaustion event" -> "the event when the database connection pool is exhausted" (or define an acronym once).
7. **Articles are mandatory.** "Check log file for error" -> "Check the log file for the error."
8. **Conditions and warnings first, as their own sentences.** "If the migration fails, the table stays locked. Run the rollback script."
9. **Don't use the same word as noun and verb nearby** ("test the test", "log the log entry"): rename one.
10. **Present tense, active voice, imperative for instructions** (matches the core rules).

## Conciseness techniques

- **Answer-first**: line 1 = the result, decision, or answer. Everything else is optional support.
- **Delete test**: for every sentence, ask "does removing this lose information?" If no, delete. A passage where a third of sentences survive deletion is filler.
- **One-pass compression targets**:
  - "in order to" -> "to"
  - "due to the fact that" -> "because"
  - "has the ability to" -> "can"
  - "a number of" -> "several" or the number
  - "at this point in time" -> now (usually delete)
  - "in the event that" -> "if"
  - "prior to" -> "before"
  - "subsequent to" -> "after"
  - "with regard to" -> "about"
  - "the majority of" -> "most"
- **Point, don't inline**: reference the file, function, diff, or doc instead of pasting or re-explaining it. "Details in `TELEMETRY.md`" beats three paragraphs.
- **Numbers over adjectives**: "cuts latency 40%" not "significantly improves performance".
- **No double introductions**: don't introduce a list ("There are three reasons. The reasons are:") twice.

## Surface checklists

### Chat / session reply
Before sending, verify:
- [ ] First line answers or states the result
- [ ] As short as the topic allows; no padding, but no artificial cap on broad topics
- [ ] Zero preamble, zero recap of the request, zero closing pleasantry
- [ ] No em dashes, no banned words, no mic drop
- [ ] Detail is pointed to, not inlined
- [ ] A reader with no context understands the essence

### Code comment
- [ ] Explains why / a non-obvious decision, not what the line does
- [ ] One line if possible; full sentences with articles if longer
- [ ] Present tense, no changelog ("2024-03: changed by X"), no dead code kept as comments
- [ ] TODOs carry an owner or ticket ID
- [ ] Consistent terminology with the surrounding code and docs

### Commit message
- [ ] Imperative subject line <= ~50 chars, no period
- [ ] Body (if any): what and why, wrapped, no slop vocabulary

### Documentation
- [ ] Full base-guide rules (see `formatting.md`)
- [ ] STE sentence/paragraph caps
- [ ] Anti-slop scan
- [ ] Essence-first ordering within each section
