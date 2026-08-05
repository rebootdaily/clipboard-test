# Clipboard v8.0.8 — Footprint Grid & Drawing Settings

Adds a lightweight reference grid and a hidden line-thickness setting to
Footprint, without adding any permanent toolbar buttons. Sketch, Photos,
dictation, badges, and the Rules engine are unaffected.

## Built in this release

- **World-space grid.** A subtle square grid renders across the infinite
  Footprint canvas — faint minor lines every 40 world units, a stronger
  major line every 5th division. It's drawn in the same world-space
  transform as strokes, so it pans and zooms together with the drawing
  exactly like a real grid would (verified: zooming 2x exactly halves the
  on-screen line count). It never touches stroke coordinates, and is
  drawn only within the current viewport's visible bounds, batched into
  two `stroke()` calls regardless of density for efficient rendering.
- **Grid is screen-only by default.** The PNG/PDF export path renders
  strokes through a completely separate offscreen canvas that never
  calls the grid-drawing function — confirmed directly in source, not
  just visually.
- **Grid On/Off**, defaulting to On, persisted in its own `localStorage`
  key (not the inspection state), so it's a device preference that
  survives Reset Inspection untouched.
- **Line thickness**: Thin (2px) / Medium (4px, default) / Thick (7px),
  persisted the same way. Applied to each new stroke at the moment it's
  drawn; strokes already on the canvas keep the thickness they were
  created with, verified after changing the setting mid-session and
  again after a full reload.
- **Drawing Settings popover** — no new permanent toolbar buttons. Opens
  via a new "⚙ Drawing Settings" entry in the existing overflow menu, or
  by long-pressing the Pencil button (500ms hold); a genuine short tap on
  Pencil still just selects the tool as before, and a long-press
  correctly suppresses the tool-switch click that follows it.

## Note on existing behavior

The request's constraints mention preserving "existing... line-
straightening behavior" — Footprint has no line-straightening today; it
was never implemented past the original Stage 1 prototype (freehand
strokes only). The per-stroke `width` field this release adds is
generic, so a future straightening feature will automatically pick up
the correct thickness with no additional plumbing.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm version 8.0.8.
3. Open Footprint — confirm the grid is visible, faint, and the toolbar
   still shows only Pencil / Eraser / Undo / Pan / More.
4. Pan and pinch-zoom — confirm the grid moves and scales with the
   drawing, not fixed to the screen.
5. Draw a stroke, export to PDF — confirm the exported image shows no
   grid lines.
6. Long-press Pencil — confirm the Drawing Settings popover opens and
   the tool doesn't change. Open it again via the overflow menu.
7. Change Line Thickness, draw a new stroke, change it again, draw
   another — confirm each stroke keeps the thickness it was drawn with.
8. Reload — confirm the Grid On/Off and Line Thickness settings, and all
   existing strokes' individual thicknesses, are all still correct.
9. Confirm Sketch, Photos, dictation, tab badges, and the Rules engine
   are all unaffected.
