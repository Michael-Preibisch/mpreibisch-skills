# Grammar and usage

## Second person
- Address the reader as *you*; the implied subject of imperatives is *you*.
- Don't use *we/our/let's* to refer to the reader or to a vague author+reader unit. *We recommend* is acceptable for genuine author recommendations, but prefer direct phrasing ("Use X").
- It's OK to use *I* only in FAQs written in the asker's voice.

## Active voice
- Default to active; name the actor: reader, server, tool, service.
- Acceptable passive: emphasize object ("The file is saved"), de-emphasize actor ("Over 50 conflicts were found"), actor irrelevant ("The database was purged in January").
- Never "is queried by you"-style passives; recast.

## Present tense
- Describe behavior in present tense: "The command creates...", "After you click Save, the dialog closes."
- Avoid *will*, *was/were* for program behavior, *would*, *should be*. Future tense only for genuinely future events from the reader's timeline that can't be recast.

## Modal verbs (word choice for recommendations and requirements)
| Meaning | Use |
|---|---|
| Ability, permission, optional action, possible outcome | can |
| Possibility, uncertain outcome | might |
| Requirement | must, you need to |
| Recommendation | we recommend / consider / it's best to (avoid bare *should*) |
| Policy/legal permission | may (only here) |
Avoid: could, should, shall, would, ought to.

## Sentence structure
- Condition/context/goal first, then instruction: "If your app runs in region X, ... :", "To start a new document, click...", "In the console, go to...".
- Include helper words: "if... then" in technical conditionals.
- One idea per sentence; break up chains of clauses; but avoid staccato fragments.
- Vary openings; don't start every sentence with "You can" or "To do".

## Articles
- Choose *a* vs *an* by sound: a URL, an HTTP request, a SQL query, an SAP system, a FHIR store.
- Don't drop articles telegraphically ("Open file" → "Open the file") outside UI labels.

## Pluralization
- Don't pluralize or possessivize code items; add a noun: "`Foo` objects", "the value of the `ADDRESS` constant".
- Plurals of abbreviations: no apostrophe (APIs, IDs, VMs, the 2000s).
- appendixes, indexes, matrixes, schemas.

## Possessives
- OK for people/organizations ("the user's password", "Google's infrastructure").
- Avoid possessives on product names, feature names, and code items; recast ("the settings of Cloud Run" → "the Cloud Run settings").

## Prepositions
- Ending a sentence with a preposition is fine if natural.
- UI: *in* dialogs/fields/lists/menus/panes/windows; *on* pages/tabs/toolbars.
- authenticate *against*; listen *on* a port; click *in* a region (not a control); more information *about* (not *on*).

## Abbreviations
- Spell out on first use with the abbreviation in parentheses — "public key infrastructure (PKI)" — unless it's more familiar abbreviated (API, HTML, REST, URL, AI, CPU, OS, SSH, IP).
- Don't create abbreviations for terms used only once or twice.
- No Latin abbreviations: e.g., i.e., etc., viz., N.B. → English equivalents.
- No internet slang: tl;dr, ymmv, aka, FYI (prose), RTFM.
- Indefinite article by pronunciation of the abbreviation: an SLA, a SQL query, an ML model... (say it out loud).
- Don't define widely known file formats; format extensions per context (a PNG file; `.png` in code font when literal).

## Capitalization
- Sentence case for headings, titles, table headers, list-item leads, navigation.
- Don't cap for emphasis; don't use ALL CAPS (except placeholders and defined UI matches).
- Follow official product-name capitalization; generic nouns lowercase (the bucket, a project, zonal persistent disk).
- After a colon: lowercase unless what follows is a complete sentence or a proper noun.
- Match UI label capitalization, except convert ALL-CAPS labels to sentence case.

## Anthropomorphism
- Systems don't *think*, *want*, *believe*, *know*, or *feel*. Prefer observable behavior: "the service retries the request", "the parser rejects invalid input".
- *lets you* is the standard replacement for "allows/enables you to".
- Avoid "the docs assume", "the app is interested in"; recast around the reader.

## Hyphens
- Prefer closed prefixed forms: *nonessential, multiregional (general), reusable, pretrained, subnetwork, autoscaling*. Exceptions kept hyphenated: *pre-existing, pre-shared, non-key, multi-cluster, multi-region (Cloud location), multi-service, multi-tenancy, self-\*, co-\* before o (co-owner)*, when the closed form creates a misread (re-create vs recreate), or before a capital (non-Google).
- Hyphenate compound modifiers before nouns: *bare-metal server, error-prone step, high-availability setup, real-time updates* — but not after (*the updates happen in real time*), and never with *-ly* adverbs (*highly available system*).
- Suspended hyphens: "two- and three-digit codes".
- Ranges in text: use *to* or *through*, not a dash ("versions 2 through 5").

## Jargon
- If the audience may not know a term, define it on first use (italics for the term being defined) or link to a definition; use it consistently after.
- Prefer plain verbs: *use* not *utilize/leverage*, *run* not *execute*, *stop* not *terminate* (unless the API term).

## Excessive claims, future features
- No superlatives or marketing (*best-in-class, blazing, revolutionary, seamless, powerful* without evidence).
- Never document unreleased functionality or hint at roadmap (*coming soon, does not yet, will support*).
- Don't claim compliance/security guarantees casually (*guarantees, ensures, 100% secure*); prefer *helps protect*, *is designed to*.
