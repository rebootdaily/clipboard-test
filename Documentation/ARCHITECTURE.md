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
VERSION                         SOURCE OF TRUTH — the app's version number,
                                 a single line, e.g. "7.1.1". Bump this by
                                 hand for each release; nothing else about
                                 versioning should be hand-edited.
generate.py                     Build script (workbook -> config.json,
                                 app_template/ -> clipboard_generated/ -> root,
                                 VERSION -> every __APP_VERSION__ token)

app_template/                   SOURCE OF TRUTH — all application code
  app.js                         Form-rendering engine + Sketch engine
  index.html                     Page shell + inline <style> + SW registration
  manifest.json                  PWA manifest
  sw.js                          Service worker — cache versioning (§9)
  styles.css                     Orphaned file, not linked from index.html
                                  (see Known Issues in ROADMAP.md)

clipboard_generated/            GENERATED — build output, wiped and
                                 recreated on every generate.py run
  app.js, index.html, manifest.json, sw.js, styles.css
                                                  (copied from app_template/,
                                                   __APP_VERSION__ stamped)
  config.json                                     (built from the workbook)

app.js, index.html,             GENERATED — published copies at repo root;
manifest.json, sw.js,           this is what a served/deployed instance
styles.css, config.json         (e.g. GitHub Pages) actually loads

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
`index.html`, `app.js`, `manifest.json`, `sw.js`, `styles.css`. This includes
100% of the Field Sketch engine, since the engine is plain JS living in
`app.js` and has no separate file of its own.

`generate.py`'s `copy_template_to_build()` copies every file in
`app_template/` into `clipboard_generated/` byte-for-byte
(`shutil.copy2`/`copytree`) — it never derives, transforms, or regenerates
any of their contents from the workbook. `publish_build_to_root()` then
copies `clipboard_generated/`'s contents to the repo root the same way.

The one exception is the literal string `__APP_VERSION__`: any occurrence of
that token in the *copied* files (currently in `index.html`, `manifest.json`,
`app.js`, and `sw.js`) is replaced with the contents of the root `VERSION`
file — see §9. `app_template/`'s own copies keep the raw token forever;
`generate.py` never writes to `app_template/`, only reads from it.

## 5. Generated files

Regenerated (or fully overwritten) every time `generate.py` runs:

| File | Regenerated from |
|---|---|
| `config.json` (root and `clipboard_generated/`) | workbook data + `VERSION` (Settings.Version) |
| `clipboard_generated/app.js`, `index.html`, `manifest.json`, `sw.js`, `styles.css` | copy of `app_template/`, `__APP_VERSION__` stamped from `VERSION` |
| root `app.js`, `index.html`, `manifest.json`, `sw.js`, `styles.css` | verbatim copy of `clipboard_generated/` |
| `VALIDATION.txt` | workbook validation results |

Note: `VERSION` itself is **not** generated — it's the one file in this
list of "don't hand-edit" territory that you deliberately hand-edit, once
per release (see §9).

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
3. `validate_workbook_structure()`: check the five required sheets and
   their required columns exist and that `APP DESIGN`/`Navigation` have
   data rows. **On failure, stop immediately** — no file is written or
   overwritten — with an itemized error in stdout and `VALIDATION.txt`.
4. `read_version()`: read and validate `VERSION`. **On failure (missing
   or empty file), stop immediately** the same way.
5. Build `cfg = {app, followups, lists, settings, navigation}`, with
   `settings.Version` set from the value read in step 4.
6. Validate `cfg`'s *content* (duplicate Field IDs, missing option lists)
   into an `issues` list — reported, but does not block generation.
7. `copy_template_to_build()`: delete and recreate `clipboard_generated/`,
   then copy every file/folder from `app_template/` into it verbatim.
8. `stamp_version()`: replace every `__APP_VERSION__` token in the text
   files just copied into `clipboard_generated/` with the real version.
9. Write `clipboard_generated/config.json` from `cfg`.
10. `publish_build_to_root()`: delete stale `app-v*.js` files at the repo
    root, then copy everything from `clipboard_generated/` to the repo root.
11. Write `VALIDATION.txt`, print a summary and the GitHub Pages URL, and
    exit `1` if there were content-validation issues, else `0`.

**Net effect**: `config.json`'s field/form data is the only thing whose
content depends on the workbook (its `Settings.Version` depends on
`VERSION` instead). Every other generated file is a verbatim copy of
`app_template/` plus a version-token substitution, so re-running
`generate.py` after only editing the workbook cannot change the Sketch
engine's behavior, and re-running it after only bumping `VERSION` cannot
change anything except the version strings.

## 8. Version stamping and offline caching

The app is installed to the home screen on iPads and used in the field,
often with poor or no connectivity, so it needs to (a) work offline and
(b) never get stuck showing a stale release once a new one ships — these
pull in opposite directions, and `app_template/sw.js` (a service worker)
is what reconciles them.

- **Cache naming**: `sw.js` names its cache `clipboard-cache-__APP_VERSION__`,
  stamped with the real version like everything else (§4). A new release
  is automatically a new, distinct cache name.
- **Fetch strategy**: every same-origin `GET` is fetched from the network
  first with `{cache:'no-store'}` (bypassing both GitHub Pages' HTTP cache
  and Safari's own aggressive disk cache for installed home-screen apps —
  this is the actual fix for "have to clear Safari website data to see
  updates"), and the response is stored in the current version's cache.
  The cache is only read from when the network fetch fails, i.e. offline.
- **Cleanup**: on `activate`, every cache whose name starts with
  `clipboard-cache-` but isn't the current version's is deleted.
  `self.skipWaiting()` (on install) and `self.clients.claim()` (on
  activate) mean a newly deployed service worker takes over immediately,
  rather than waiting for every open tab/home-screen session to fully
  close first.
- **Page-side registration** (in `index.html`, right after the `app.js`
  script tag): registers `sw.js` with `updateViaCache:'none'` (so the
  browser always fetches `sw.js` itself fresh when checking for updates,
  rather than potentially reusing a cached copy of the service worker
  script) and calls `registration.update()` on every load. It also listens
  for `controllerchange` and reloads the page — but only if this page
  already had a controller before (i.e. this is a genuine version change,
  not the very first time the service worker is ever installed), so a
  first-time visitor never sees an unexplained extra reload.

In practice: because fetches are network-first, a plain refresh already
gets the newest `index.html`/`app.js`/`config.json` whenever the device is
online, independent of the service worker's own update cycle. The service
worker's job is (1) making sure `VERSION` gets you a genuinely new network
request instead of a cached one in the first place, and (2) keeping a
current, single-version cache around so the app still works with no
connectivity at all.

**Testing caveat**: service workers require a secure context — HTTPS, or
`http://localhost`. Testing over the LAN via a PC's IP address (as
described in `CONTRIBUTING.md` for iPad testing) will **not** register a
service worker, since that's plain HTTP to a non-localhost host. Service
worker behavior can only be verified via `http://localhost` locally, or
against the real HTTPS GitHub Pages URL.

## 9. Git workflow

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

## 10. Safe editing workflow

**Never edit these directly** — the next `generate.py` run silently
overwrites them:

- `config.json` (root and `clipboard_generated/`)
- Everything under `clipboard_generated/`
- Root-level `app.js`, `index.html`, `manifest.json`, `sw.js`, `styles.css`
- `VALIDATION.txt`

**Edit instead:**

- `Clipboard_v4_Master_Base.xlsx` — for inspection form content (fields,
  options, visibility rules, tab order)
- `VERSION` — bump this by hand for every release; it's the one file in
  the "edit instead" list rather than the "never edit" list above
- `app_template/app.js`, `app_template/index.html`,
  `app_template/manifest.json`, `app_template/sw.js`,
  `app_template/styles.css` — for **all** application code, including the
  Sketch engine and the service worker/cache-versioning logic (§8)

Then either run `generate.py` (requires the workbook present) to copy
`app_template/` through to `clipboard_generated/` and root, stamp
`__APP_VERSION__`, and regenerate `config.json`, or — if neither the
workbook nor `VERSION` is being touched — mirror the changed
`app_template/` file(s) into `clipboard_generated/` and root by hand, as
was done for the v7.1.1 fix.

**The workflow, step by step:**

1. Decide which source you're changing: the workbook (form content) or
   `app_template/` (application code, including the Sketch engine). Never
   both files of a pair (e.g. `app_template/app.js` and root `app.js`) —
   pick the `app_template/` one and let the tooling/copy step propagate it.
2. Make the edit only in the source file.
3. Run `py -3 generate.py` (or `Start_Clipboard_v4.bat`) to regenerate
   `config.json` and republish `app_template/` through to
   `clipboard_generated/` and root — or, if only testing without the
   workbook available, copy the changed `app_template/` file(s) to
   `clipboard_generated/` and root by hand.
4. Confirm the three copies of each touched file (`app_template/`,
   `clipboard_generated/`, root) are identical again (`diff`) before
   committing.
5. Review `git status`/`git diff` — `generate.py` has no git awareness and
   will overwrite root/`clipboard_generated/` unconditionally.
