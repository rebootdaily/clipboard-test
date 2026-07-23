# Clipboard v8.0.0 — Office Efficiency

## Built in this release

- Added an **Office Summary** tab before Review.
- Added copy-ready blocks for:
  - Property + Site
  - Condition + Updates
  - Deficiencies + Follow-ups
  - Complete inspection summary
- Added **Print / PDF** from the Office Summary.
- Added required-item alerts to the Office Summary.
- Added room and photo totals to the Office Summary.
- Added notes, flags, and photo counts beside summarized fields.
- Selecting **Other** now automatically opens and focuses the related note field.
- Opening Notes now automatically places the cursor in the note field.
- Added voice dictation buttons for field notes when browser speech recognition is available.
- Added separate **Camera** and **Gallery** photo controls.
- Preserved the stabilized Field Sketch engine.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm version 8.0.0.
3. Select Other and confirm the note field opens with keyboard focus.
4. Test Notes and voice dictation on the iPad.
5. Test Camera and Gallery separately.
6. Enter sample inspection data and open Office Summary.
7. Test all four copy buttons.
8. Test Print / PDF.
9. Confirm sketch behavior remains unchanged.
