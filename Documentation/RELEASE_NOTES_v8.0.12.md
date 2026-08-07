# Clipboard v8.0.12 — Compact Two-Column PDF/Print Layout

Reworks the Office Summary's print/PDF CSS so standard field/value data
renders as a genuine two-column grid, instead of the previous CSS
multi-column layout whose full-width escape hatch never actually fired.
Screen/on-device layout is untouched — this is print CSS and the
long-value/notes detection logic only.

## What changed

**`app_template/app.js`** — `renderOfficeSummary()`'s row template. The
`.office-row` class expression that used to add `has-note` only when a
field had a note now adds `wide` when the field has a note **or** its
value is longer than 40 characters:

```js
// before
`office-row ${x.flag?'office-flagged':''} ${x.note?'has-note':''}`
// after
`office-row ${x.flag?'office-flagged':''} ${x.note||String(x.value||'').length>40?'wide':''}`
```

`has-note` is gone entirely — `wide` is now the single class that
triggers full-width spanning, and it's the one class the CSS actually
matches (see below).

**`app_template/index.html`** — the `@media print` block:

- `.office-rows` switched from `column-count:2` (CSS multi-column,
  which flows content top-to-bottom per column and only pairs rows
  side-by-side by coincidence) to `display:grid;grid-template-columns:1fr 1fr`
  (true two-column grid, each row occupies one grid track, left/right
  pairing is now structural, not incidental).
- `.office-row.wide{grid-column:1/-1}` replaces the old
  `.office-row.has-note,.office-row.wide{column-span:all}`. This is the
  fix for a dead rule: nothing in the JS ever added a `wide` class
  before this release, so `column-span:all` never fired for anything
  except noted rows — long values with no note always got squeezed into
  a half-width column and wrapped.
- Card decluttering that earlier "compact PDF" rounds missed:
  `.office-stats>div` and `.office-alert` still carried a full
  `border`/`background`/`border-radius` in print. Both are now flat —
  `.office-alert` keeps only a 3px left accent border as a callout, no
  box. `.office-row` and `.follow-line` no longer inherit the screen-mode
  `border-bottom` divider into print.

Section headings (`Property`, `Site`, `Exterior`, `Interior`,
`Mechanical`, …), the Footprint/Sketch export section, and the Photos
section were already siblings of `.office-rows` rather than children of
it, so they were already full-width by DOM structure — confirmed, not
changed.

## Long-value handling

A field is forced full-width (`grid-column:1/-1`) when either is true:

- it has a note attached, or
- its value text is longer than 40 characters

40 characters was chosen because it's roughly the point where a value
starts wrapping to 2+ lines inside a ~360px print column at 9.5pt —
past that point, a single full-width line reads better and takes less
vertical space than a wrapped narrow one.

## Verification

Tested directly against the rendered print CSS (extracted the actual
`@media print` rule text from the stylesheet and re-applied it live
under `@media screen` to measure real layout, rather than trusting the
CSS unverified):

- **Column pairing**: adjacent field rows land at the same `top` with
  `left` offsets of 0 and ~643px — genuine side-by-side grid pairing,
  confirmed across Property, Site, and Exterior sections.
- **Wide-row spanning**: a synthetic 100+ character value and a synthetic
  noted field both got the `wide` class and rendered at full container
  width (1265px in the test viewport), then the grid correctly resumed
  normal two-column flow on the next row — no leftover dead column.
- **Card declutter**: computed styles confirm `.office-row`,
  `.office-stats>div`, `.office-alert`, and `.follow-line` all have
  `border: 0` (`.office-alert` keeps only its left accent) and
  `break-inside: avoid`.
- **Section/Sketch/Photos full width**: confirmed via `getBoundingClientRect()`
  that section `<h3>` headings and an injected test Footprint sketch
  block both render at full container width, sitting outside
  `.office-rows`.
- **Page-count comparison**: reconstructed the previous (`column-count:2`)
  CSS and JS class logic from `git diff` and rendered the same test
  content (Property/Site/Exterior/Mechanical with a long value, a noted
  field, and a synthetic Footprint image) at the Letter-page usable width
  (739px = 8.5in − 0.8in margins @ 96dpi) side by side with the new
  layout. Total height came out close for this dataset (old ≈2662px vs
  new ≈2593px, both 2 pages at the 979px-usable-height page estimate) —
  the win here isn't a dramatic page reduction, it's correctness: under
  the old CSS the long, un-noted value got squeezed into a 359px column
  and wrapped to 56px tall; under the new CSS the same value spans the
  full 739px width as a single 39px-tall line. The old multi-column rows
  also don't reliably line up as left/right pairs at all — multi-column
  balances the whole flowed section, not row by row.
- **Regressions**: reloaded fresh at v8.0.12, walked Sketch, Footprint,
  Photos, and Office Summary tabs — zero console errors, no visual or
  functional change to on-screen layout.

## Test checklist

1. Regenerate with `python generate.py`.
2. Confirm version 8.0.12 in the header and page title.
3. Fill in a simple inspection (a handful of Property/Site fields) and
   open Office Summary → Print / PDF. Confirm fields pair up two per
   line under each section heading.
4. Add a long text value (40+ characters) to any field and a note to
   another. Confirm both render full-width in the print view, and that
   normal two-column pairing resumes immediately after each.
5. Fill in a complex inspection — most tabs, a Footprint sketch, and a
   few photos — and print. Confirm section headings, the Footprint
   image, and the Photos grid all span the full page width, while short
   field/value pairs stay two-column.
6. Confirm no leftover card borders/backgrounds in the printed stats
   tiles, incomplete-items alert, or follow-up lines.
7. Confirm Sketch, Footprint, Photos, dictation, and the Rules engine
   are unaffected on-screen.
