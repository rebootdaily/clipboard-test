# Clipboard v8.0.13 — Exit Interview Quick Resolution / Disregard

Adds a one-tap way to resolve an Exit Interview follow-up item that
doesn't apply, without typing anything. This is an app usability change
only — no workbook schema, trigger definitions, or Rules syntax were
touched, and it works generically with any current or future
`FOLLOW_UP` group the workbook generates.

## Root cause

The Exit Interview badge previously counted every unanswered follow-up
*field* with no way to mark one as intentionally not applicable short of
typing something into it (or "N/A") just to silence the alert. Two
follow-on problems made this worse: the badge counted at the field
level rather than the card level, so a single irrelevant group (e.g. a
group with 5–10 fields) could inflate the count by that many; and there
was no persisted concept of "the appraiser looked at this and it
doesn't apply," so the only way to clear an alert was to enter data.

## Follow-up status data model

Status is tracked per **Follow-Up Group** — the heading the appraiser
sees (e.g. "Kitchen", "Roof") — not per individual field, because a
single group in this workbook commonly bundles several fields (the real
data averages ~5 fields/group, up to 10 for "General"). One Disregard
tap resolves the whole card, matching one badge decrement.

`state.followUpStatus` only stores an explicit override:

```json
{ "Roof": "disregarded", "Solar": "unable_to_verify" }
```

"Open" and "Answered" are never written — they're derived:

```js
followUpGroupStatus(group) =
  overrideStatus(group)                         // 'disregarded' | 'unable_to_verify' | none
  ?? (everyFieldInGroupAnswered(group) ? 'answered' : 'open')
```

This means filling in a normal response still requires zero extra taps
(item 7), and reopening a group just deletes the override key — nothing
about the group's actual field values is ever touched.

## Badge-counting logic

`dynamicBadgeCounts()`'s Exit Interview branch now counts distinct
**open** groups instead of unanswered fields:

```js
const countedGroups = new Set();
CFG.followups.forEach(f => {
  const group = f['Follow-Up Group'];
  if (!activeGroups.has(group) || countedGroups.has(group)) return;
  if (followUpGroupStatus(group) !== 'open') return;
  countedGroups.add(group);
  bump('Exit Interview');
});
```

Verified live: a fresh inspection with General + Kitchen active showed
badge `2` (not the ~15 individual unanswered fields those two groups
contain). Disregarding one group dropped it to `1` immediately, with no
re-render delay.

## Disregard / Unable to Verify implementation

Each open follow-up card in the Exit Interview tab gets two buttons
beneath its fields:

```html
<button class="follow-resolve-btn disregard">✓ Disregard</button>
<button class="follow-resolve-btn unable">Unable to Verify</button>
```

Tapping either calls `setFollowUpGroupStatus(group, status)`, which
writes the override, saves, and re-renders — no confirmation dialog, no
required text. The card is removed from the main list on that same
render and its heading/fields never disappear from `state`; only the
status overlay changes.

## Reopen implementation

Resolved groups collapse into a "Resolved / Disregarded (N)" toggle at
the bottom of the tab. Expanding it lists each resolved group with a
Reopen button that deletes the override (`setFollowUpGroupStatus(group,
'open')`) — no confirmation, immediate badge increase, and the group
reappears inline with every previously entered value intact.

## Persistence

`state.followUpStatus` rides the same `localStorage` save/load path as
the rest of inspection state — no new storage layer. Verified: after
disregarding 5 groups and reloading the page, all 5 statuses persisted,
the badge stayed correct, and none of the disregarded groups reappeared
as new alerts.

## PDF handling

- `renderOfficeSummary()`'s "N required item(s) incomplete" alert and
  the Review tab's incomplete-item list both skip required-but-empty
  fields belonging to a disregarded or unable-to-verify group — verified
  with a temporarily-forced Required field in a disregarded group
  (didn't appear) alongside one in an open group (did appear, as a
  sanity check).
- Disregarded groups are fully excluded from the printed "Deficiencies
  & Follow-ups" section — verified the section renders with zero
  mention of 4 disregarded test groups.
- Unable-to-verify groups print as `GroupName: Unable to Verify` in
  that same section — verified this is the *only* line that appears for
  an unable-to-verify group with no other flag/note/value.

## Mobile / touch test results

Verified in this environment's Chromium-based preview only (no access
to real Safari/iPadOS or Samsung/Android hardware — flagging this as a
limitation, not a pass):

- Real click dispatch (not synthetic event injection) on the Disregard
  button resolved the card on the **first** tap — no focus-then-activate
  double-tap step, matching the fix already in place for field
  activation (FN-011).
- 5 rapid sequential disregards each decremented the badge exactly once
  with no lag, no dialogs, and no console errors.
- At a 375×812 mobile viewport, Disregard/Unable to Verify buttons
  render at 172×44px and the Reopen button at 44px tall — this rounds
  bumped Reopen from 36px to 44px to match the app's existing touch
  target convention (found during this testing pass, not requested).

## Files modified

- `app_template/app.js` — follow-up status helpers
  (`followUpGroupFields`, `followUpGroupAnswered`, `followUpOverrideStatus`,
  `followUpGroupStatus`, `setFollowUpGroupStatus`), `dynamicBadgeCounts()`,
  `fieldTabHtml()` (Exit Interview card/resolve/collapse markup),
  `wireFollowUpControls()` (new), `render()`, `renderReview()`,
  `renderOfficeSummary()`, initial `state` shape, `init()`'s load/merge.
- `app_template/index.html` — new CSS for `.follow-resolve-row`,
  `.follow-resolve-btn`, `.follow-status-tag`, `.follow-resolved-*`,
  `.follow-reopen-btn`.
- `VERSION` — `8.0.12` → `8.0.13`.

## Remaining limitations

- Touch testing was done in a single Chromium-based emulated environment;
  Test G's Safari/iPadOS and Samsung/Chrome-on-Android passes could not
  be run for real and should be spot-checked on actual devices.
- The workbook's follow-up fields currently have zero fields marked
  `Required = Yes`, so the required-field-override behavior (item 8) was
  verified by temporarily forcing `Required` on a field at runtime
  rather than against a real required follow-up field — worth a manual
  re-check once/if a real required follow-up field exists.
- "Answered" groups are not moved into the "Resolved / Disregarded"
  panel (only explicit Disregard/Unable-to-Verify overrides are) — this
  was a deliberate choice so a fully-answered card stays inline and
  directly editable, rather than requiring the appraiser to dig into a
  collapsed panel to fix a typo. Flagging this since the original
  mockup showed an answered item inside that panel too.

## Test checklist

1. Regenerate with `python generate.py`.
2. Confirm version 8.0.13 in the header.
3. Open Exit Interview with several triggered groups. Confirm the badge
   equals the number of open *groups*, not raw fields.
4. Tap Disregard on one card — confirm it disappears immediately, badge
   drops by 1, no dialog, no text required.
5. Disregard several more rapidly — confirm each is a single tap with
   no lag.
6. Open "Resolved / Disregarded," tap Reopen on one — confirm it returns
   to the main list with prior values intact and the badge increases.
7. Enter a partial answer in an open card, then Disregard it — confirm
   the entered value survives if you Reopen it later.
8. Reload the page after disregarding several items — confirm none
   reappear as new alerts.
9. Confirm the source walkthrough field that triggered a group (e.g.
   Kitchen Updated?) is unchanged after disregarding that group.
10. Print/export Office Summary — confirm disregarded groups don't
    appear in Deficiencies & Follow-ups, and unable-to-verify groups
    appear as `Group: Unable to Verify`.
11. Confirm Sketch, Footprint, Photos, Review, and normal walkthrough
    tabs are unaffected.
