# Word list (condensed)

Source: https://developers.google.com/style/word-list, with this skill's exceptions applied.
Entries whose only rationale was the guide's inclusive-language policy are **omitted on purpose** — do not enforce them. That means these stay as written: *whitelist, blacklist, graylist, master, slave, kill, abort, nuke, blast radius, man-hours, man-in-the-middle, manned, manpower, manmade, guys, male/female adapter, sanity check, sane, grandfathered, dummy variable, gendered pronouns (he/she/his/her), black/white/gray hat, black-box/white-box testing terms, STONITH, war room, brown bag, dogfood.*

If a term isn't listed here, fall back to Merriam-Webster (first-listed spelling) and general clarity.

## A
- **a/an** — choose by the next word's *sound*: an SAP system, a SQL query ("sequel"), an FHIR → no, *a FHIR* ("a fire"), an HTTP request, a URL.
- **abnormal/deficient/deformed** — OK for systems.
- **about vs. on** — "more information *about* X", not *on*.
- **above/below** — don't use for doc position (*earlier*/*preceding*, *later*/*following*), version ranges (*later*/*earlier*), or UI position (rewrite without direction). OK non-directionally (hierarchy, "below zero").
- **access (verb)** — prefer *see*, *view*, *edit*, *use*, *find*.
- **actionable** — avoid; *useful*, *that you can act on*.
- **ad hoc** — OK in data contexts; no hyphen, no italics.
- **admin** — write out *administrator* unless it's a UI label (Android: *admin* OK).
- **agnostic** — avoid; *platform-independent*.
- **aka** — don't use; *also known as*, or parentheses.
- **allows you to** — don't use; *lets you*.
- **alpha/beta** — lowercase unless part of a product name.
- **AM/PM** — caps, no periods, preceding space: 9:00 AM.
- **and/or** — avoid outside tables.
- **and so on** — avoid (see *etc.*).
- **anti-pattern** — avoid; name the specific bad practice.
- **API** — not for a single method or class.
- **app vs. application** — *app* for end-user programs; *application* OK for enterprise complexity and set phrases.
- **appendixes** — not *appendices*.
- **as** — if you mean *because*, write *because*.
- **as of this writing / currently / presently / at present / now / soon / eventually / in the future / does not yet** — delete; write timelessly.
- **authenticate vs. authorize** — users authenticate; requests are authorized. Preposition: authenticate *against*.
- **authN/authZ** — don't use.
- **auto\*** — usually closed: *autohealing, autopopulate, autoscaling, autotagging*. But *automatically update*, not *autoupdate*.

## B
- **backend** — one word. **bare metal** (noun) / **bare-metal** (adj).
- **best effort** — avoid; be specific.
- **between vs. among** — *between* for distinct things (even 3+); *among* for group members.
- **big-endian / little-endian** — hyphenated, lowercase.
- **boolean** — code font + exact keyword casing for the type; *Boolean* for logic/math.
- **button** — press mechanical buttons; tap on-screen ones; a link isn't a button.

## C
- **can / could / may / might / must / should / would** — *can*: ability, permission, option, possible outcome. *might*: possibility/uncertainty. *must* (or *you need*): requirement. *may*: policy/legal only. Avoid *could*, *should*, *shall*, *would*.
- **cell phone** — *mobile phone* / *mobile device* / *phone*. Same for *cellular data/network* → *mobile data/network*.
- **chapter** — only for books; otherwise *document*, *page*, *section*.
- **check / uncheck / deselect** — don't use for checkboxes; *select* and *clear*.
- **checkbox** — one word.
- **choose vs. select** — *select* for UI elements; *choose* generic.
- **CLI** — don't use generically; name the specific CLI.
- **click** — not *click on*. Hyphenate *right-click*, *double-click*. Android: *tap*.
- **click here** — never; use descriptive link text.
- **codebase, codelab** — one word.
- **comprise** — don't use; *consists of*, *contains*, *includes*.
- **config** — spell out *configuration* in prose; verbatim for code items.
- **cons/pros** — *disadvantages*/*advantages*.
- **console** — always name it (the Google Cloud console); *the* before it.
- **copy and paste** — avoid as instruction; say what to enter.
- **CPU** — all caps, no expansion needed.
- **crazy/insane** — *complicated*, *unexpected* (for things).
- **Create a new X** — usually just *Create an X*.
- **curl** — not *cURL*.

## D
- **dash** — an em dash is not a hyphen; don't call hyphens dashes.
- **data** — singular mass noun: *the data is*, *less data*.
- **data center, data source, data type** — two words. **datastore, dataflow** (stream-processing sense) — one word. *data flow* if you mean flow of data.
- **deprecate** — means "recommend against use", not *removed*.
- **desire/desired** — *want*, *that you want*.
- **dialog** — the UI element (not *dialog box*, *pop-up*); *dialogue* only for conversation.
- **directory vs. folder** — CLI context: directory; GUI: folder; default: directory.
- **disable/disabled** — for UI state prefer *turn off*, *deactivate*, *unavailable*, *inactive*; don't use for "broken".
- **display** — transitive only: "the area appears" or "the area displays the image", never "the area displays".
- **documentation/document** — *this document*, not *this article/topic/doc*.
- **drag** — not *click and drag*, not *drag and drop* (adjective *drag-and-drop* OK).
- **drop-down** — usually omit; *list* or *menu*.

## E
- **e.g.** — *for example* or *such as*. **i.e.** — *that is*.
- **each** — not a synonym for *all*.
- **earlier/later** — for version ranges (not *lower/higher*, not *2.2+*); for doc position (not *above/below*).
- **easy/easily/simple/simply/quick/quickly/just** — delete.
- **ecommerce, email** — no hyphen, lowercase e. Don't verb *email*; "send email".
- **either** — parallel syntax; two options.
- **enable** — for features/APIs OK; for people use *lets you* ("The API lets you...", never "enables/allows you to").
- **endpoint, emoji (pl. emoji)** — as shown.
- **enter vs. type** — *enter* for putting text in fields; *type* when literal keystrokes matter; press `Enter` explicitly when needed.
- **etc.** — avoid; restructure with *such as* / *including*. If unavoidable, *etc.* with period.
- **execute** — prefer *run*.
- **exploit** — only in the security sense; not "use".
- **extract** — not *unarchive/uncompress/untar/unzip*.

## F
- **fail over** (verb) / **failover** (noun, adj).
- **filename** — one word. **file system** — two.
- **fill in** (fields) / **fill out** (forms).
- **fintech, ad tech** — spell out on first mention.
- **following** — "the following table:" — fine as noun phrase.
- **foo/bar/baz** — avoid; meaningful placeholder names.
- **for example** — followed by comma; not *for instance*.
- **frontend** — one word.
- **functionality** — often just *features* or *capabilities*.

## G–H
- **Google Cloud** — not GCP. **gcloud CLI** — full name *Google Cloud CLI* on first mention.
- **hang/hung** — *stop responding*, *not responding*.
- **hardcode/hardcoded** — no hyphen.
- **healthcare** — one word.
- **healthy/health check** — prefer concrete states (*responsive*); *health check* only if it's the UI/API term.
- **high availability** (noun) / **high-availability** (adj); HA after first use. Same pattern: *load balancing* / *load-balancing*.
- **hit** — not for *click/press/type*.
- **hostname** — one word.
- **hover** — don't use; *hold the pointer over* (waiting for UI) or *point to*.
- **HTTPS** — not HTTPs.

## I–K
- **ID** — not Id/id (outside code).
- **impact** — noun only; verb → *affect*.
- **in order to** — *to* (keep only if needed for clarity).
- **index** — plural *indexes* (unless math/finance).
- **ingest** — only when significant processing; else *import/load/copy*.
- **inline** — one word.
- **interface** — noun only; not a verb.
- **internet** — lowercase.
- **jank/janky** — only the graphics-glitch sense.
- **k8s** — don't use; *Kubernetes*.
- **kebab case** — *dash-case*.
- **key** — not as adjective meaning "crucial"; qualify which key (API key, encryption key).
- **key-value pair** — hyphenated (contrast *key pair* in crypto).

## L–N
- **learnings** — *knowledge*, *lessons*.
- **left-nav / right-nav** — *navigation menu*.
- **legacy** — define it; no pejorative use.
- **let's** — don't use.
- **leverage / utilize** — *use* (or *build on*).
- **lifecycle** — one word.
- **like vs. such as** — both OK for examples/comparisons.
- **login** (noun/adj) / **log in** (verb) — but prefer **sign-in / sign in**; *sign in to*, never *sign into*. **sign-out / sign out**.
- **long-running operation** — hyphenated; LRO after first use.
- **matrixes** — not *matrices* (unless math).
- **method** — don't also use generically for "approach" in OO contexts.
- **microservices, namespace, N/A (spell out first), name server (two words), NoSQL** — as shown.
- **mobile** — not a standalone noun.
- **native** — for software prefer *built-in*; *cloud-native* is ambiguous.
- **neither ... nor**.
- **new/newer/old/older** — avoid for products/versions; use version numbers with *earlier/later*.
- **nonce** — define on first use; technical contexts only.

## O–P
- **OAuth 2.0** — exactly.
- **off-the-shelf/COTS** — *ready-made*, *prebuilt*, *standard*.
- **omnibox** — *address bar*.
- **once** — if temporal, use *after*.
- **on-premises** — never *on-prem*, *on premise*, *on-premise*.
- **OS** — OK.
- **out of the box** — literal use only.
- **page** — web pages and console subpages.
- **path** — not *filepath*, *file path*, *pathname*.
- **per** — rates only (requests per day); else *according to*, *for each*.
- **performant** — avoid; say what's good (fast, accurate).
- **persist** — not transitive ("to make the token persistent", not "to persist the token").
- **plain text** — two words (*plaintext* only in crypto).
- **please** — no.
- **plugin** (noun) / **plug-in** (adj) / **plug in** (verb).
- **pop-up/popup** — don't use; *dialog* or *menu*.
- **populate** — systems populate; people *fill in*.
- **possible/impossible** — not for *you can/can't*.
- **postmortem** — prefer *retrospective* (DR/DevOps: *blameless postmortem* OK).
- **pre\*** — usually closed: *prebuilt, prerecorded, preemptible, presubmit, precapture*. Exceptions: *pre-existing, pre-shared key*.
- **press** — keys and mechanical buttons (*press* `Control+C`); *tap* for on-screen.

## Q–S
- **quota** — prefer the specific limit type when possible.
- **RDP/SSH** — not verbs: "connect using SSH", never "SSH into".
- **regex** — *regular expression*.
- **repo** — *repository*.
- **REST** — don't expand the acronym.
- **review** — only for critical reading; otherwise *read*.
- **RFC 2318** — with space.
- **roll out** — define or replace with *gradual/in stages*.
- **runbook** — one word.
- **runtime** (environment) / **run time** (moment during execution).
- **scale** — always with direction/magnitude (*scales up quickly*), never bare "at scale".
- **screenshot** — noun only; "take a screenshot".
- **scroll** — prefer *go to*; no *scroll up/down*.
- **see** — OK for links ("For more information, see X").
- **select** — menus items, options, checkboxes; **clear** to unmark.
- **setup** (noun/adj) / **set up** (verb).
- **SHA-1**, **single sign-on**, **NoSQL** — as shown.
- **shall** — no.
- **since** — if causal, use *because*.
- **spin up** — *create* or *start*.
- **startup** (noun/adj) / **start up** (verb).
- **status bar** — two words.

## T–Z
- **tap** — Android/touch; **touch & hold** (not *long press*).
- **tarball** — *tar file*.
- **third-party** (adj) / **third party** (noun).
- **timeframe** — avoid; *period*, *schedule*, or specific duration.
- **timeout** (noun/adj) / **time out** (verb). **timestamp** — one word.
- **tl;dr, ymmv, RTFM** — never.
- **toolbar, tooltip, touchscreen, username, wildcard, whitepaper, website** — one word. **web page** — two words.
- **toggle** — noun only; "click the **X** toggle to the on position"; the verb is *turn on/turn off*.
- **turn on / turn off** — good default verbs for features/settings; pair consistently (not *turn on* ... *disable*).
- **type** — see *enter*.
- **US** — OK as adjective/abbreviation (not *U.S.*); don't say *America* for the US.
- **v/versus** — spell out *versus* in prose; *vs.* only where space-limited.
- **via** — avoid; *by using*, *through*.
- **want vs. wish/desire** — *want*.
- **web page** vs **website** — two words / one word.
- **whether vs. if** — *whether* for alternatives ("whether the flag is set"); *if* for conditionals; *whether or not* only when "regardless" is meant.
- **while** — temporal only; contrast → *although*, *whereas*.
- **Wi-Fi** — hyphenated, capitalized.
- **will** — avoid; present tense.
- **workaround** (noun) / **work around** (verb).
- **workflow** — one word.
- **zero out** — prefer *set to zero*.
