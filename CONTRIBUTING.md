# Contributing to Clipboard

This is the day-to-day workflow for developing Clipboard. For the deeper
"why" behind the structure described here, see [ARCHITECTURE.md](ARCHITECTURE.md)
and [ROADMAP.md](ROADMAP.md) — this document is the practical how-to.

## 1. Project architecture (short version)

- **The workbook** (`Clipboard_v4_Master_Base.xlsx`) is the source of truth
  for the **inspection forms** — Property, Site, Exterior, Interior,
  Mechanical, Photos, Exit Interview, Review. Its `APP DESIGN`,
  `FOLLOW-UP TEMPLATES`, `Lists`, `Settings`, and `Navigation` sheets are
  compiled by `generate.py` into `config.json`.
- **`app_template/`** is the source of truth for **all application code** —
  the page shell, styling, and every tab's rendering logic, including the
  entire Field Sketch (drawing) engine. Nothing in the Sketch tab is
  workbook-driven.
- **Generated files** are build artifacts, produced fresh by `generate.py`
  every run: `config.json`, everything under `clipboard_generated/`, and
  the published root copies of `app.js`/`index.html`/`manifest.json`/
  `styles.css`, plus `VALIDATION.txt`. None of these should be hand-edited.

Full details, including exactly how the Sketch engine is kept decoupled
from the workbook, live in [ARCHITECTURE.md](ARCHITECTURE.md).

## 2. Safe editing workflow

### Which files to edit

| To change... | Edit... |
|---|---|
| Inspection form fields, options, visibility rules, tab order | `Clipboard_v4_Master_Base.xlsx` |
| Anything in the app shell, styling, or the Sketch engine | `app_template/app.js`, `app_template/index.html`, `app_template/manifest.json`, `app_template/styles.css` |
| The build/generator itself | `generate.py` |

### Which files to never edit directly

- `config.json` (root and `clipboard_generated/`)
- Anything under `clipboard_generated/`
- Root-level `app.js`, `index.html`, `manifest.json`, `styles.css`
- `VALIDATION.txt`

Any of these will be silently overwritten the next time `generate.py` runs.
If you find yourself editing one of them, stop and make the same change in
`app_template/` (or the workbook) instead.

### How to regenerate the application

```
py -3 generate.py
```

(or double-click `Start_Clipboard_v4.bat`, which runs `generate.py` and
then serves the result). This reads the workbook, validates its structure
first (see §4 below — a malformed workbook stops generation with no files
touched), rebuilds `config.json`, copies `app_template/` into
`clipboard_generated/`, and publishes `clipboard_generated/` to the repo
root. Check `VALIDATION.txt` and the console output afterward.

If you only changed `app_template/` and don't have the workbook handy (or
don't want to touch `config.json`), you can mirror the changed file(s) into
`clipboard_generated/` and root by hand instead — just make sure all three
copies end up identical (`diff` them) before committing.

### How to test locally on PC

1. Run `py -3 generate.py` (or `Start_Clipboard_v4.bat`).
2. Serve the output: `Start_Clipboard_v4.bat` does this automatically via
   `py -3 -m http.server 8000` from `clipboard_generated/`, opening
   `http://localhost:8000`. You can also serve the repo root the same way
   if you're testing the published copy directly.
3. Open the URL in a desktop browser. Use devtools' device toolbar/touch
   emulation to approximate an iPad Mini 6 viewport (744×1133 portrait /
   1133×744 landscape) as a quick first pass — this catches layout and
   overflow issues, but **cannot** substitute for real pointer/pencil
   input testing (see below).

### How to test locally on iPad

Real hardware is required for anything touching pointer events, gestures,
or the Sketch tab — desktop browsers cannot faithfully emulate Apple
Pencil input, multi-touch gesture arbitration, or Safari's native
scroll/zoom behavior.

1. Start the local server on your PC as above, but bind/serve so it's
   reachable on your LAN (the built-in `http.server` already listens on
   all interfaces; find your PC's LAN IP with `ipconfig`).
2. On the iPad, open Safari and navigate to `http://<your-PC-LAN-IP>:8000`.
3. Optionally use Share → Add to Home Screen to test the installed PWA
   experience (matches `manifest.json`).
4. Run the Sketch tab's acceptance test (see the relevant
   `README_V*_FIELD_SKETCH.txt`/`README_V*_REFACTORED_SKETCH.txt` for the
   current one): continuous Pencil/finger drawing to `pointerup`,
   two-finger pan, pinch-zoom, object select/move/resize, text edit and
   reload-persistence.

### Git branch workflow

- `main` holds the last known-good, deployable state.
- Any change beyond a trivial documentation fix goes on its own feature
  branch, named for what it does (e.g. `v7.1-input-engine`).
- Don't commit work-in-progress or unreviewed changes directly to `main`.
- Keep a feature branch focused on one piece of work; don't pile unrelated
  changes onto it.

### Commit guidelines

- Write commit messages that explain *why*, not just *what* — the diff
  already shows what changed.
- Release-marking commits follow the repo's existing `vX.Y.Z <summary>`
  convention (see `git log` for examples).
- One logical change per commit; prefer several small, clear commits over
  one large one when a branch does more than one thing.
- Never amend or force-push shared/pushed history unless explicitly asked.
- Never bypass hooks (`--no-verify`) to force a commit through.

### When to merge into main

Only after:

1. The change has been tested locally (PC at minimum; iPad hardware for
   anything touching Sketch/input).
2. For Sketch/input changes specifically, the acceptance test has passed
   on a real iPad Mini 6.
3. The branch has been reviewed (via a Pull Request — see below).
4. Explicit approval to merge has been given — merges are never automatic,
   even after tests pass.

## 3. Release workflow

The full path from idea to shipped change on `main`:

1. **Feature branch** — cut from `main`, named for the work
   (`git checkout -b vX.Y-description`).
2. **Local testing** — run `generate.py`, serve locally, exercise the
   change in a desktop browser.
3. **iPad testing** — for anything touching Sketch/input/gestures, run the
   acceptance test on a real iPad Mini 6 over the LAN as described above.
4. **Git commit** — commit with a clear, why-focused message following the
   conventions above.
5. **Push branch** — `git push -u origin <branch-name>`.
6. **Pull Request** — open a PR from the branch into `main` describing what
   changed, why, and how it was tested (PC/iPad/acceptance test results).
7. **Merge to main** — only after review and explicit approval; `main`
   should only ever move forward via a reviewed PR, not a direct push.

## 4. Workbook validation

`generate.py` validates the workbook's *structure* (required worksheets,
required columns, and minimum data rows) before building anything. If the
workbook fails this check, generation stops immediately with a clear error
listing exactly what's missing — no `config.json`, no
`clipboard_generated/`, and no published root files are touched. Existing
content-level checks (duplicate Field IDs, option lists referenced but not
defined) still run afterward and are reported in `VALIDATION.txt`, but
don't block generation the way a structural failure does.
