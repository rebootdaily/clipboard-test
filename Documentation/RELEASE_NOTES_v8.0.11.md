# Clipboard v8.0.11 — Add "Street Scene" to GuidedPhotoCategory

Adds "Street Scene" to the workbook's `GuidedPhotoCategory` list, the
source list for the photo quick-label chips added in v8.0.10.

## Workbook change

Added as a new row (row 16, column BB) in the Lists sheet, appended
after the existing 14 values rather than inserted mid-list. In this
workbook's raw XML format, every cell encodes its own row number, so a
true mid-list insertion would require renumbering every row below it
across the *entire* sheet (all columns, not just this one) — a
disproportionate risk for adding one value. Verified before touching the
real file: row 16 didn't exist for any column yet, so this was a pure
addition touching nothing else. Edited via direct, byte-precise
modification of the workbook's internal XML (not a full rewrite), and
verified against `generate.py`'s own reader before and after replacing
the real file.

## Test checklist

1. Regenerate with `python generate.py` (already done for this release).
2. Confirm version 8.0.11 in the header.
3. Open a photo in the Photos editor — confirm "Street Scene" appears as
   a quick-label chip.
4. Confirm no other list, tab, or field changed.
