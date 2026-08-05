# Clipboard v8.0.6 — Streamlined Photo Workflow

Rebuilds photo capture and storage around field-testing feedback:
"Capture first. Organize later." No workbook, generator, Rules engine,
Footprint, or dictation changes.

## Built in this release

- **Photo capture is now instant and uninterrupted.** Taking or importing
  a photo from any field's camera/gallery action saves it immediately —
  no label prompt, no caption prompt, no category prompt, no confirmation
  dialog. The appraiser is returned straight to the inspection.
- **Structured photos automatically inherit their field's label.** A
  photo taken from a field labeled "X Photo" gets a default label of "X"
  (the trailing word "Photo" is stripped); any other field's label is
  used as-is. The field's Section (falling back to its Tab) becomes the
  photo's category — no new workbook column was added for this.
- **Free/untethered photos** captured via the existing "Free Shoot Photo
  Inbox" field are automatically labeled "Additional Photo 1", "Additional
  Photo 2", etc., and can be renamed later from the Photos page.
- **Photos page redesigned** into a review/organize screen: a responsive
  thumbnail grid (2 columns on phone, 3 on tablet, responsive on desktop)
  showing each photo's preview, current label, source field/category, and
  a caption indicator. The existing capture fields on that tab
  ("Free Shoot Photo Inbox", "Guided Photo Checklist") are unchanged and
  still work exactly as before.
- **Photo editor** (opened only by intentionally tapping a thumbnail —
  never automatically after capture): edit the label, add an optional
  longer caption, reassign the photo to a different field/category,
  reorder it earlier/later, replace the underlying image, delete it, or
  view it full-screen.
- **New photo data model** (`state.photoRecords`): each photo has a
  stable unique ID, independent of its position in any list — labels,
  captions, categories, and order all stay attached to the correct photo
  through reload, reordering, replacing, and PDF export. A photo's
  storage bytes live in the same IndexedDB blob store introduced in
  v8.0.5; existing photos from before this release are migrated
  automatically the first time the app loads, with no data loss.
- **PDF export** now prints each photo individually in its saved order,
  with its resolved label (user label → inherited field label → category
  → "Additional Photo") and caption if present, kept together on the
  page. Unlabeled free photos still print, as "Additional Photo N" — they
  are never silently dropped.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm version 8.0.6.
3. Take a photo from any field's camera icon — confirm no dialog appears
   and the app stays on the current tab.
4. Open the Photos page and confirm that photo's thumbnail shows the
   field's label.
5. Capture a photo from "Free Shoot Photo Inbox" — confirm it's labeled
   "Additional Photo N"; rename it and reload to confirm the rename
   persists.
6. Take ten photos in quick succession — confirm zero modal interruptions
   and that all ten appear with unique IDs.
7. Edit a label/caption and reorder a photo, reload, and confirm all
   three persist correctly.
8. Export to PDF with a mix of structured and free photos — confirm every
   photo appears with its correct label and caption attached.
9. Confirm Sketch, Footprint, dictation, tab badges, and the Rules engine
   are all unaffected.
