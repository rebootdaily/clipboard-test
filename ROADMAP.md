# Clipboard Inspection App — Roadmap

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces referenced below
fit together.

## Current Version

**v7.1.1** — "Stabilize iPad sketch input and gestures"
Branch `v7.1-input-engine`, commit `62c5a66`. Acceptance-tested on a real
iPad Mini 6. **Not yet merged to `main`.**

## Completed Milestones

- **v4.x** — Base inspection workflow: Property, Site, Exterior, Interior,
  Mechanical, Photos, Exit Interview follow-ups, Review.
- **v5.0** — Sketch Engine introduced.
- **v6.0** — Point-to-point sketch.
- **v6.1** — Guide points.
- **v6.2** — Closure assist.
- **v6.3** — Geometry assist beta.
- **v6.4** — Smart Sketch beta; **v6.4.1** point tools restored;
  **v6.4.2** precision cutouts; **v6.4.3** smart auto-close.
- **v7.0** — Corrected version; object-based Field Sketch engine
  introduced (freeform pencil/line/arrow/circle, editable objects).
- **v7.0.1** — Sketch interaction fix.
- **v7.1.0** — Refactored Sketch: current `fs*` engine, editable text/
  dimensions/notes, duplicate/delete, high-contrast outdoor buttons,
  object-based save/load with migration from v7 strokes.
- **v7.1.1** — iPad input engine stabilization: canvas clipping and
  touch-action CSS (the missing `.fs-stage`/`.fs-stage canvas` rules),
  `preventDefault()` parity across all pointer handlers. Verified: canvas
  no longer overflows its container in portrait or landscape, two-finger
  pan, pinch-zoom, and continuous Pencil/finger strokes to `pointerup`.

## Known Issues

- The legacy point-to-point sketch code (~100 lines in `app.js`) is dead —
  unreachable because a later `renderSketch()` declaration shadows it.
  Harmless, but adds file size and can confuse future readers.
- `styles.css` (root and `app_template/`) is not linked from `index.html`
  and has been orphaned since before v7.1; all live styling is inline in
  `index.html`'s `<style>` block. Anyone editing `styles.css` expecting it
  to affect the app will be surprised that it does nothing.
- `sketch_chunk.txt` / `snippet.txt` at the repo root are tracked-but-unused
  development scratch files, not referenced by `generate.py` or any app
  file.
- The Field Sketch canvas bitmap is a fixed 1600×1100 while its display box
  has a different aspect ratio, causing mild non-uniform x/y scaling.
  Cosmetic only — the coordinate math (`fsMetrics`/`fsScreen`/`fsWorld`)
  already compensates correctly for drawing/hit-testing accuracy.
- Theoretical edge case: a second finger tapping a structural UI button
  (e.g. Undo, Add Page) while the other hand is mid-stroke would trigger a
  canvas-recreating `renderSketch()` call and could interrupt that stroke.
  Not reproduced in testing; not yet guarded against.
- `generate.py` hardcodes `settings['Version'] = '7.0'` in `build_config()`,
  so `config.json`'s app version can lag behind the actual shipped
  `index.html`/`app.js` version strings (currently 7.1.1).

## Next Milestones

- Merge `v7.1-input-engine` into `main` once broader field testing (beyond
  the single acceptance pass) confirms stability across more appraisers/
  devices.
- Decide the fate of the dead point-to-point sketch code: remove it, or
  keep it deliberately for reference/rollback.
- Resolve the `styles.css` orphan question: either delete the file or wire
  it back in and de-duplicate it against `index.html`'s inline styles.

## Future Ideas

- Keep `generate.py`'s `settings['Version']` in sync with the app's actual
  version automatically instead of hardcoding it.
- Add an automated smoke test for the generator pipeline (a scripted
  version of the dry-run verification performed manually this session:
  confirm `app_template/` output is byte-identical after a build, confirm
  `config.json` is the only file that changes).
- Now that `ARCHITECTURE.md` formalizes the app_template/config.json
  boundary, consider extracting the Field Sketch engine into its own file/
  module so the "never touches `CFG`" guarantee is structurally enforced
  rather than only documented.
- Clean up `sketch_chunk.txt`/`snippet.txt` once confirmed to have no
  historical value worth keeping.
