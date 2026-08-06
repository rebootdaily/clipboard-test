# Clipboard v8.0.10 — Photo Quick-Label Chips

Adds quick-label chips to the Photos review editor. Capture itself is
completely unaffected — chips only exist inside the editor, which is only
reachable by intentionally tapping a thumbnail on the Photos page.

## A note on sourcing

The request asked for a workbook list named "PhotoQuickLabels" — that
list doesn't exist. The workbook already has `GuidedPhotoCategory`
(Street Left, Street Right, Across, Front, Rear, Left Side, Right Side,
Kitchen, Bathroom, Electrical Panel, HVAC, Water Heater, Pool, Other),
already wired as the Options list for the "Guided Photo Checklist"
field. Flagged this rather than guessing; confirmed with the user to use
`GuidedPhotoCategory` rather than inventing or renaming a workbook list
myself.

## Built in this release

- **Quick-label chips** in the photo editor, sourced from
  `GuidedPhotoCategory`. Tapping a chip populates the editable Label
  input and commits it, exactly as if the appraiser had typed it —
  nothing is forced or pre-selected on open.
- **Manual editing preserved**: the label field remains a normal text
  input after a chip is tapped. Verified directly — selecting "Kitchen"
  then typing " - North Wall" afterward correctly produces
  "Kitchen - North Wall", not just "Kitchen".
- **Recent-use order persists** in its own `localStorage` key (not
  inspection data), most-recently-used first. To avoid chips visibly
  jumping around while the appraiser might tap another one, the new
  order only takes effect the *next* time the editor opens for any
  photo — not immediately during the same interaction. Verified surviving
  both same-session reopen and a full page reload.
- **No interruption to capture**: camera/gallery capture (structured or
  free) still saves instantly with zero dialogs — chips have no
  connection to that code path at all.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm version 8.0.10.
3. Capture a photo (camera or gallery) — confirm no prompt appears.
4. Open it from the Photos page — confirm quick-label chips appear.
5. Tap a chip — confirm the Label field updates immediately and the chip
   highlights.
6. Type additional text after tapping a chip — confirm it appends rather
   than being overwritten.
7. Close and reopen the same (or another) photo's editor — confirm the
   just-used chip now appears first.
8. Reload the app — confirm the chip order and the edited label both
   persist.
9. Confirm Sketch, Footprint, dictation, and the Rules engine are
   unaffected.
