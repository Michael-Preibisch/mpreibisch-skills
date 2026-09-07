# Design guidance

General craft for a shareable HTML page, written for a host that provides no artifact
design or diagramming skill of its own. It is independent guidance, not a copy of any
host's design skill. Where a host does provide one, load that too and treat it as
supplemental: [SKILL.md](../SKILL.md) still decides.

## Pick the right form

One question, one form. Do not draw a diagram for something a sentence answers.

| The reader needs to see | Use |
| --- | --- |
| Two or more options against the same criteria | A table, one row per option |
| How a quantity changes, splits, or compares | A chart |
| How a system works, what calls what, what owns what | A diagram |
| An ordered set of steps or states | A numbered list, or a diagram when branches exist |
| One number that carries the point | A sentence in the answer box |

If a table would need more than about eight columns, split it. If a diagram would need
more than about a dozen nodes, split it into stages and show one per section.

## Layout

- One column. Let the page scroll.
- Give the visual room: full content width, generous space above and below.
- Two levels of heading, at most three. Deeper nesting means the page should be split.
- Keep line length readable. Long prose in a narrow measure beats edge-to-edge text.
- Group related content in a card. Do not nest cards inside cards.
- Space carries hierarchy better than borders, weight, or size. Reach for space first.

## Type and colour

- Two sizes for body text at most: normal, and one smaller for muted supporting lines.
- Weight, not colour, separates a label from its value.
- Colour encodes category or state. It never encodes order or importance.
- Two or three colours carry a whole diagram. A fourth usually means the diagram is
  doing two jobs.
- Every colour comes from a token in the page shell, so both themes stay correct.
- Never use colour alone to carry meaning: pair it with a label, shape, or position.

## Accessibility

- Semantic HTML: real headings, lists, tables with `th`, `button` for actions.
- Every control is reachable and operable from the keyboard, with a visible focus state.
- Every meaningful image or diagram carries a text description that states what it
  shows, not what it is. A decorative graphic is marked as decorative.
- Body text meets normal contrast in both themes. Check muted text in dark mode: it is
  the first thing that fails.
- Do not convey state through colour alone in charts. Label the series directly where
  space allows.

## Inline SVG

- Always set `viewBox`. Never set a fixed pixel `width` and `height` on the root `svg`.
- Lay the diagram out on a deliberate grid. Do not let nodes land wherever the maths puts them.
- Nodes never overlap. Labels never clip their box, never overlap an edge, never run off the canvas.
- Every edge is labelled with what actually crosses it: a call, a message, a data type,
  a direction of ownership. An unlabelled arrow states nothing.
- Name the actors with the names they carry in the system. Draw the boundaries the
  system actually has, and label them.
- Text inherits the token colours through the shell's `svg text` rule. Strokes and
  fills use `var(--token)`, never a literal hex.
- Give the whole figure a `role="img"` and an accessible name, or a caption directly
  under it.

## Charts

- Pin the library version exactly and load it from a CDN the host allows, before the
  inline script that uses it.
- Read colours from the computed token values, not from literals.
- Listen for the shell's `themechange` event and restyle the chart when the theme flips.
  A chart that stays light-styled in dark mode is the most common failure.
- Label the axes and state the units. A number with no unit is not evidence.
- Start a bar-chart value axis at zero. A truncated axis misleads.
- Hand-write inline SVG instead when the page must render with no network.

## Diagram content

- Draw the mechanism that exists, from the code, config, or manifest that defines it.
  Never from a plan or a ticket description.
- Show the path that actually runs, including the failure path when it matters.
- Leave out anything the reader does not need to answer the page's question.
- One diagram answers one question. Two questions means two diagrams.

## Before you ship

- Read the page at a narrow viewport. Nothing overflows sideways; wide tables and
  diagrams scroll inside their own container.
- Read the page in light and in dark. Check the diagram strokes, the chart colours, the
  muted text, and any border that only shows up in one theme.
- Read every string as a stranger would. Any term a zero-context teammate would stop at
  is defined before it is used.
