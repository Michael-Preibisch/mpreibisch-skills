# Formatting and organization

## Headings and titles
- Sentence case; no end punctuation; no ampersands (*and*); no code font unless the heading is a code item (then backticks are OK).
- Task headings: bare imperative or gerund per doc-set convention ("Create an instance" / "Creating an instance" — be consistent); conceptual headings: noun phrases.
- Don't stack headings with no text between; don't skip levels; avoid "Introduction"/"Overview" as the only H2 when avoidable.
- "Optional:" style applies to steps; for optional sections say who can skip and why in the intro.

## Lists
- Numbered = ordered sequence. Bulleted = unordered set. Description list = term + definition (bold run-in headings OK: **Term**: description).
- Never a one-item list.
- Intro is a complete sentence ending with a colon (or period if material intervenes). Never a fragment completed by the items ("Use the button to: • submit..." is wrong).
- Parallel grammar across items.
- Capitalization/punctuation: capitalize first word; end with a period if the item contains a verb or is a sentence; no period for single words, fragments without verbs, all-code items, or pure link/title items; make the whole list consistent.
- Run-in headings: **Bold term**: lowercase description after a colon (period → capital). No dashes as separators.
- In-sentence lists: serial comma; never end with *etc.* — introduce with *such as* / *including* instead.

## Procedures
- Numbered steps; sub-steps a., b., then i., ii.
- Single-step procedure → one bulleted item, not "1.".
- One user action per step; combine tiny sequential menu picks with **A > B**.
- Imperative first verb in every step. Complete sentences.
- Location before action: "In the **X** window, click **Y**."
- Goal before action: "To save the file, click **Save**." Required-but-goal-labeled steps: "Sort the data: ..." colon form.
- Action then result, same paragraph: "Click **Run**. The results appear." Don't pre-announce dialogs then repeat them.
- Optional steps: "Optional: ..." (not "(Optional)").
- No *please*, no keyboard shortcuts as primary instructions, no "run the following command:" filler — describe what the command does ("Deploy the load generator:").
- Document only the best way when multiple exist; prefer keyboard-accessible, shortest path.
- Reference repeated procedures by link instead of restating.

## UI elements
- Bold every named element exactly as labeled: buttons, menus, fields, dialogs, tabs, checkboxes, panes. ALL-CAPS labels → sentence case.
- Element nouns: window, page (web/console), dialog (not pop-up), pane/panel (not section/area for panes), section (labeled group), menu + command (not menu item/choice), navigation menu (not nav bar/pane), toolbar, tab, box/field (Cloud & Workspace: *field*), list, combo box, spin box, checkbox, radio button, expander arrow (not zippy/expando), toggle.
- Verbs: click (desktop; never *click on*), tap (touch), select/clear (checkboxes, options), enter (text into fields), type (literal keystrokes), press (keys: press `Control+C`), choose (generic), drag, turn on/turn off, point to / hold the pointer over (not *hover*), go to.
- Menu paths: **File > New > Document** — single bold span; in HTML add `aria-label="and then"` around `>`.
- Buttons with icons: icon + tooltip name ("click ⋮ **More**"), never "the three-dot icon". Drop trailing ellipses from labels ("Click **Browse**").
- No directional language (*left-hand side*, *above*, *below*); add context, tooltip names, or a screenshot instead.
- Don't verb UI labels ("**Name** the account" → "In the **Name** field, enter...").
- Keyboard keys: `kbd`/code font, uppercase letters, spelled-out modifiers, `Modifier+Key` (no spaces): `Control+Shift+P`; macOS variant in parentheses.

## Code in text
Code font (backticks) for: filenames, extensions, paths, directories; commands, flags, utility names (`kubectl`); class/method/function names; attributes and values; env vars; data types, keywords, enums; database rows/columns; HTTP verbs, status codes (`404 Not Found`), `Content-Type` values; DNS record types; port numbers; IP addresses in technical context; query params; strings used in code/commands; text the user types; placeholders.

Regular font for: product/service/org names, domain names in prose, URLs meant to be visited (make them links with descriptive text).

Rules:
- No quotation marks around code (unless part of the code).
- Don't inflect code items; attach a noun and inflect that ("`Job` objects", "send a `POST` request").
- Method names without class prefix unless ambiguous (`get`, not `animal.get`).
- Status codes: "an HTTP `400 Bad Request` status code"; ranges "`2xx`".
- Code-styled UI element → bold + code.
- Command-line: don't invent a `$` prompt inside copyable commands; show output separately; introduce commands by what they do.

## Placeholders
- ALL_CAPS_SNAKE_CASE, code font (+ italics in HTML where supported): `PROJECT_ID`.
- Explain every placeholder right after the command: "Replace the following:" with a description list, or "Replace `NAME` with ...".
- Meaningful names, not `foo`/`xxx`.

## Links and cross-references
- Link text = page title or a meaningful description; never *click here*, *this document*, *here*, or a raw URL as text.
- Standard phrasing: "For more information about X, see [Title]." (about, not on).
- Punctuation outside the link text. Don't italicize/quote titles when linked.
- Tell readers when a link leaves the current doc set or downloads a file.
- Cross-reference format for sections: "see [Section name] in this document" or "on the X page".

## Numbers
- Spell out zero–nine; numerals 10+; numerals always for: units of measurement, versions, page/chapter/step numbers, technical quantities, decimals, negatives, percentages (use %: 5%), dimensions, ranges with units.
- Don't start a sentence with a numeral — recast or spell out.
- Consistent treatment within a category in one context ("5 cats and 12 dogs").
- Thousands separators (commas) for 4+ digits (10,000) — but never in code, ports, addresses, years.
- Very large: mix numeral+word (2 billion) or exact numerals.
- No plural apostrophes (the 1990s, CPUs).
- Fractions: spell out in prose (two-thirds) or decimals with units.

## Dates and times
- Unambiguous dates: month name spelled out — January 19, 2025 (or 19 January 2025 for some locales); never 01/19/25.
- Weekday, Month D, YYYY when weekday needed.
- Times: 9:00 AM, 24-hour OK if consistent; include time zone when relevant (10:00 AM Pacific Time).
- Durations: use words or units (30 seconds, 2 hours), ranges: "from 9:00 to 10:00 AM".
- Prefer relative-free, timeless phrasing (no *recently*, *today* in evergreen docs).

## Units of measurement
- Space between number and unit: 64 GB, 2.5 GHz, 100 ms (exception: %, °).
- Rates with *per* in prose (requests per second); slash only where space-constrained; Mbps/MBps not Mb/s.
- Don't pluralize unit symbols (5 kg, not kgs).

## Punctuation
- **Commas**: serial comma always; comma after intro phrases ("For example, ..."); comma before *and then* in compound imperatives ("Click **A**, and then click **B**"); comma splices never.
- **Colons**: introduce lists/blocks; lowercase after unless full sentence follows; one space after.
- **Semicolons**: sparingly; consider splitting sentences.
- **Dashes**: em dashes are banned (see plain-language.md). Use a comma, colon, period, or parentheses. Hyphens in compound modifiers are unaffected.
- **Ellipses**: avoid in prose; drop from UI labels.
- **Exclamation points**: avoid.
- **Parentheses**: OK for asides; don't nest; punctuation inside only for full-sentence parentheticals.
- **Periods**: one space after; inside quotation marks (American style); no periods in headings; end punctuation outside link text; "etc." keeps its period.
- **Quotation marks**: double quotes, American placement (periods/commas inside); use for titles of short works; not for emphasis, not around code.
- **Slashes**: avoid *and/or*, avoid slash-as-or (write *or*); OK in paths, URLs, fractions; no spaces around.
- **Ampersand**: *and*, except in UI labels/code that literally use &.

## Notes and notices
- Use sparingly; one notice type per purpose:
  - **Note**: helpful aside.
  - **Caution**: proceed carefully; potential problem.
  - **Warning**: danger of data loss, security exposure, or money.
  - **Key Point / Key Term / Tip / Success** as supported by the doc system.
- Don't stack multiple notices; don't put required steps inside notes.

## Tables
- Use tables for multi-property structured data; lists for single-dimension items.
- Sentence-case headers; no empty header cells; introduce the table ("The following table describes...:"); don't merge cells; align content types consistently.

## Examples
- Introduce with "for example," or "the following example shows..."; keep example values realistic and use reserved example domains (example.com, example.org) and RFC 5737 IPs (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24) and E.164 example numbers; never real customer data.

## Images
- Provide alt text describing function/content; don't rely on color or position; introduce figures in text ("The following diagram shows..."); no "as shown above".

## Accessibility quick hits
- No directional-only instructions; no sensory-only descriptions; meaningful link text; parallel list items; define abbreviations; keyboard-first procedures.
