# Clipboard v8.0.1 — Field Testing Fixes

Patch release addressing issues found during live field testing on iPad Mini
and Samsung Galaxy, plus a prototype module. No workbook, generator, or
Dynamic Follow-Up/Visibility Rule changes.

## Built in this release

- Added an isolated **Footprint** Stage 1 prototype tab: infinite-canvas
  freehand sketching (pencil, eraser, undo, pan, pinch-zoom, autosave with
  drawing/zoom/pan restoration). Lives beside the existing Sketch tab;
  Sketch is untouched and remains the default.
- Fixed the bottom navigation bar being clipped on iPad Mini — the viewport
  meta tag was missing `viewport-fit=cover`, so `env(safe-area-inset-bottom)`
  was always `0` and existing safe-area padding did nothing.
- Nav tabs keep their names (no icons), with larger touch targets and
  horizontal scrolling for all 10 tabs.
- Reduced field clutter: action icons (note/dictate/camera/gallery/flag)
  are hidden until the field is interacted with, then reappear automatically
  on any tap/focus inside that field — not just a small icon area. Fields
  with existing notes/photos/flags show a compact indicator chip instead of
  the full toolbar when idle. Only one field's toolbar is shown at a time.
- Counter controls (`- value +`) restyled as one grouped pill instead of
  three disconnected pieces.
- **Fixed dictation getting stuck in a listening state** (FN-001): the mic
  button now doubles as an always-visible Stop control, `onerror`/`onend`
  both independently reset UI state, a 15s hard timeout backstops a hung
  recognizer, and tab switches, screen lock, and moving to another field
  all force-stop an in-progress session.
- **Fixed dictation writing into the wrong field** (FN-006): dictation is
  now bound to an explicit initiating field ID rather than a DOM node
  reference, session handoff between fields is properly sequenced
  (stop-and-confirm before starting the next), and a field that disappears
  mid-session stops dictation with a non-blocking message instead of
  redirecting text elsewhere.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm the header shows version 8.0.1.
3. Confirm the bottom nav bar is fully visible (not clipped) on iPad Mini,
   with all 10 tabs reachable by scrolling.
4. Tap into a field via a text box, a choice/toggle button, a counter, and
   a checkbox — confirm the action toolbar appears each time, and only for
   that field.
5. Dictate into two different fields in sequence; confirm each field only
   ever receives its own dictated text.
6. Start dictation, then switch tabs / lock the screen / tap another field
   — confirm dictation stops cleanly every time, with no stuck listening
   state.
7. Confirm Sketch and the new Footprint prototype both still work
   independently.
