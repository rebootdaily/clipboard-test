# Clipboard Inspection App — Architecture

This document describes how the codebase is put together, which files are
authoritative, which are build artifacts, and how the Field Sketch engine is
kept isolated from the workbook-driven inspection forms.

## 1. Overall application architecture

Clipboard is a single-page Progressive Web App with no framework and no
bundler: a static `index.html`, a single `app.js`, and a JSON config file,
served as-is (locally via a static file server, or via GitHub Pages). The
primary target device is an iPad Mini 6.

The app has two independent domains that share one UI shell but must never
depend on each other:

1. **Inspection Forms** — the Property, Site, Exterior, Interior, Mechanical,
   Photos, Exit Interview, and Review tabs. Their fields, labels, options,
   visibility rules, and navigation order are all *data*, loaded at runtime
   from `config.json`.
2. **Field Sketch** — the Sketch tab. A hand-written, self-contained drawing
   engine with its own state, storage, and rendering. It reads **zero**
   fields from `config.json`.

`state.activeTab==='Sketch'` is special-cased in `render()` before any
config-driven lookup happens, and `buildTabs()` unconditionally force-injects
the "Sketch" tab into the nav bar regardless of what the workbook's
Navigation sheet contains. This is what guarantees domain #2 can never be
affected by changes to domain #1's data source.

## 2. Folder structure

```
Clipboard_v4_Master_Base.xlsx   SOURCE OF TRUTH — inspection form content
generate.py                     Build script (workbook -> config.json,
                                 app_template/ -> clipboard_generated/ -> root)

app_template/                   SOURCE OF TRUTH — all application code
  app.js                         Form-rendering engine + Sketch engine
  index.html                     Page shell + inline <style>
  manifest.json                  PWA manifest
  styles.css                     Orphaned file, not linked from index.html
                                  (see Known Issues in ROADMAP.md)

clipboard_generated/            GENERATED — build output, wiped and
                                 recreated on every generate.py run
  app.js, index.html, manifest.json, styles.css   (copied from app_template/)
  config.json                                     (built from the workbook)

app.js, index.html,             GENERATED — published copies at repo root;
manifest.json, styles.css,      this is what a served/deployed instance
config.json                     (e.g. GitHub Pages) actually loads

VALIDATION.txt                  GENERATED — build/validation report

README_V*.txt                   Hand-written release notes, one per
                                 shipped version (historical record)
INSTALL.txt, Start_Clipboard_v4.bat   Manual local-run instructions/script

sketch_chunk.txt, snippet.txt   Tracked but unused scratch/draft leftovers
                                 from earlier sketch-engine iterations; not
                                 referenced by generate.py or any app file
```

## 3. Source of truth: the workbook

`Clipboard_v4_Master_Base.xlsx` has five sheets that `generate.py` reads:
`APP DESIGN`, `FOLLOW-UP TEMPLATES`, `Lists`, `Settings`, `Navigation`. These
become `config.json`'s `app`, `followups`, `lists`, `settings`, and
`navigation` keys — nothing else. This is the **only** source of truth for
inspection form content: field labels, input types, option lists, visibility
rules, display order, and tab order for the non-Sketch tabs.

The workbook has no sheet, cell, or setting that feeds the Sketch tab in any
way. Editing it and re-running `generate.py` only ever changes `config.json`.

## 4. Source of truth: `app_template/`

`app_template/` is the only place application **code** should be edited —
`index.html`, `app.js`, `manifest.json`, `styles.css`. This includes 100% of
the Field Sketch engine, since the engine is plain JS living in `app.js` and
has no separate file of its own.

`generate.py`'s `copy_template_to_build()` copies every file in
`app_template/` into `clipboard_generated/` byte-for-byte
(`shutil.copy2`/`copytree`) — it never derives, transforms, or regenerates
any of their contents from the workbook. `publish_build_to_root()` then
copies `clipboard_generated/`'s contents to the repo root the same way.

## 5. Generated files

Regenerated (or fully overwritten) every time `generate.py` runs:

| File | Regenerated from |
|---|---|
| `config.json` (root and `clipboard_generated/`) | workbook data |
| `clipboard_generated/app.js`, `index.html`, `manifest.json`, `styles.css` | verbatim copy of `app_template/` |
| root `app.js`, `index.html`, `manifest.json`, `styles.css` | verbatim copy of `clipboard_generated/` |
| `VALIDATION.txt` | workbook validation results |

None of these should ever be hand-edited — the next `generate.py` run
silently overwrites any manual change to them.

## 6. Sketch engine architecture

`app.js` currently contains **two** sketch implementations:

1. **Legacy "point-to-point" engine** (roughly lines 62–159): `sketchTool`,
   `sketchAuxTool`, `wireSketch()`, `drawSketch()`, `beginPoint()`, etc.,
   targeting `#sketchCanvas`. This code is **dead** — it declares its own
   `function renderSketch(){...}`, but a second `renderSketch` is declared
   later in the file (function-declaration hoisting means the last one
   wins), so this whole block is unreachable at runtime. It is harmless but
   inert; see ROADMAP.md for its disposition.

2. **Active "Field Sketch" engine** (roughly lines 180–231, marked
   `/* Clipboard 7.1.0 Refactored Field Sketch */`): `fsTool`, `fsDraft`,
   `wireFieldSketch()`, `fsDraw()`, etc., targeting `#fieldSketchCanvas`
   inside `.fs-stage`. This is what actually renders when
   `state.activeTab === 'Sketch'`.

Key properties of the active engine:

- **State**: `state.fieldSketch = { activePageId, pages: [{ id, name,
  objects[], background, viewport:{scale,x,y} }] }`, persisted to
  `localStorage` alongside the rest of app state. It never reads or writes
  `CFG` (the object built from `config.json`).
- **Canvas lifecycle**: one `<canvas id="fieldSketchCanvas" width="1600"
  height="1100">` per page. `renderSketch()` rebuilds `#screen`'s `innerHTML`
  (recreating the canvas element) only on explicit structural actions —
  adding/deleting a page, undo/redo swapping the whole sketch snapshot,
  selecting a different page. It is never called automatically (no
  timers, no resize/orientation listeners), so a stroke in progress is
  never interrupted by a canvas recreation.
- **Input**: unified Pointer Events (`pointerdown`/`pointermove`/`pointerup`/
  `pointercancel`/`lostpointercapture`) registered on the canvas with
  `{passive:false}`, `preventDefault()` on every handler, and explicit
  `setPointerCapture`/`releasePointerCapture`. A single active pointer
  draws/selects/erases; two simultaneous pointers drive pan + pinch-zoom
  (`fsGesture`). `getCoalescedEvents()` is used for smooth Apple Pencil
  sampling.
- **CSS dependency**: `.fs-stage`, `.fs-stage canvas`, `.field-sketch-card`,
  `.fs-toolbar`, etc. must be defined in `index.html`'s inline `<style>`
  block (not in `styles.css`, which is orphaned — see ROADMAP.md). This is
  what clips the canvas to its container and sets `touch-action:none` so
  Safari's native scroll/zoom doesn't fight the custom gesture handlers.
  This was the root cause fixed in v7.1.1.

## 7. Generator workflow

Running `generate.py` does, in order:

1. Print the generator banner (workbook source / app source / generated
   output / warning not to hand-edit generated files).
2. Read the workbook's five sheets.
3. Build `cfg = {app, followups, lists, settings, navigation}`.
4. Validate `cfg` (duplicate Field IDs, missing option lists) into an
   `issues` list.
5. `copy_template_to_build()`: delete and recreate `clipboard_generated/`,
   then copy every file/folder from `app_template/` into it verbatim.
6. Write `clipboard_generated/config.json` from `cfg`.
7. `publish_build_to_root()`: delete stale `app-v*.js` files at the repo
   root, then copy everything from `clipboard_generated/` to the repo root.
8. Write `VALIDATION.txt`, print a summary and the GitHub Pages URL, and
   exit `1` if there were validation issues, else `0`.

**Net effect**: `config.json` is the only artifact whose *content* depends
on the workbook. Every other generated file is a verbatim copy of
`app_template/`, so re-running `generate.py` after only editing the
workbook cannot change the Sketch engine's behavior.

## 8. Git workflow

- `main` is the last known-good, deployable state.
- Larger changes (like the iPad input-engine work) happen on a dedicated
  branch (e.g. `v7.1-input-engine`) and are merged to `main` only after
  explicit review/approval — never automatically.
- Repo history shows one commit per shipped version (`vX.Y.Z <summary>`),
  though a branch may accumulate more than one commit before merge.
- `generate.py`'s publish step writes directly to the repo root with no
  git awareness. After running it locally, review `git status`/`git diff`
  before committing — it will happily overwrite uncommitted local edits
  at the root.
- Never run `generate.py` against a repo state where `app_template/` is
  stale relative to root/`clipboard_generated/` — whatever is currently in
  `app_template/` becomes the new root and `clipboard_generated/` content.

## 9. Files that should never be edited directly

- `config.json` (root and `clipboard_generated/`)
- Everything under `clipboard_generated/`
- Root-level `app.js`, `index.html`, `manifest.json`, `styles.css`
- `VALIDATION.txt`

**Edit instead:**

- `Clipboard_v4_Master_Base.xlsx` — for inspection form content (fields,
  options, visibility rules, tab order)
- `app_template/app.js`, `app_template/index.html`,
  `app_template/manifest.json`, `app_template/styles.css` — for **all**
  application code, including the Sketch engine

Then either run `generate.py` (requires the workbook present) to copy
`app_template/` through to `clipboard_generated/` and root and regenerate
`config.json`, or — if the workbook isn't being touched — mirror the
changed `app_template/` file(s) into `clipboard_generated/` and root by
hand, as was done for the v7.1.1 fix.
