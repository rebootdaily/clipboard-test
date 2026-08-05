# Clipboard v8.0.7 — Dynamic Field Highlighting & Guided Attention

Enhances the Dynamic Rules system so tab badges are no longer the only
cue — once a tab is open, newly revealed questions are easy to spot
without any dialog, forced navigation, or interruption to the inspection.
No workbook, Rules worksheet, Visibility Rule syntax, Footprint, PDF
export, Photos, dictation, or navigation changes.

## Built in this release

- **Section highlighting.** A section is given a subtle amber background
  and border only while it contains at least one dynamically revealed,
  unanswered field. Reuses the app's existing warning-accent color
  (`--warn` / `#d7a900`), so it reads as "Clipboard," not a bolted-on
  effect.
- **Per-field NEW badge.** Each dynamically revealed, unanswered field
  shows a small "NEW" chip next to its label. It disappears the moment
  that specific field is answered — independently of the other fields in
  its section.
- **Section highlight clears automatically** once every dynamically
  revealed field within it has been answered; badges and highlights are
  removed together, with no stale state left behind if the triggering
  value changes back (e.g. Occupancy Vacant → Owner).
- **Optional auto-scroll**: tapping a tab's badge specifically (not the
  tab label itself) smoothly scrolls to the first NEW field on that tab.
  Manually opening a tab never forces a scroll.
- **No new field-level state to persist.** Whether a field is "new" is
  computed fresh from its current Visibility Rule result and answered
  status on every check — there's no separate "have I shown NEW for this
  yet" flag to keep in sync across reload/restore, which is what makes
  Test 6 (restore doesn't resurrect stale NEW indicators) hold
  automatically rather than needing its own bookkeeping.
- **Works for any future dynamic rule with no additional code** — the
  highlighting reads the same Resolved Visibility Rule / answered-state
  data the tab badges already use, so a brand new rule like
  `POOL_PRESENT` or `WATERFRONT` gets the same treatment automatically.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm version 8.0.7.
3. Set Occupancy to Owner — confirm no highlights anywhere.
4. Set Occupancy to Vacant, open Mechanical — confirm the Utilities
   section is highlighted and Water On / Electric On / Gas On all show
   NEW.
5. Answer Water On — confirm only its NEW badge disappears, the section
   stays highlighted, and the Mechanical badge count drops by one.
6. Answer the remaining Utilities fields — confirm the section highlight
   clears and the Mechanical badge disappears.
7. Set Occupancy back to Owner — confirm Utilities hides with no leftover
   highlight state.
8. Reload the app — confirm previously answered fields stay answered
   with no NEW badge, and genuinely unanswered visible fields still
   correctly show NEW.
9. Confirm Sketch, Footprint, dictation, Photos, PDF export, and the
   Rules engine are all unaffected.
