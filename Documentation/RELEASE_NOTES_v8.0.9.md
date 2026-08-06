# Clipboard v8.0.9 — Fix Field-Button Double-Tap Defect (FN-011)

High-priority responsiveness fix: a single tap on any field control now
both activates the field and applies the value, instead of requiring a
second tap.

## Root cause

Field activation (revealing the note/dictate/camera/flag toolbar) was
triggered on `pointerdown`, before the tap's `click` event fired. Making
the toolbar visible toggles `.tools` from `display:none` to
`display:flex`, which is a real layout change — measured directly: it
shifted a choice button ~9.6px down the moment the field activated.

On a real touchscreen, that shift happens *while the finger is still
down*, between touchstart and touchend. The button the finger landed on
is no longer in the same place by the time the tap ends, so the browser's
hit-testing doesn't register a click on it — only the *second* tap, once
the field is already active and nothing moves, lands correctly. This also
explains why it wasn't reproducible with simple synthetic `click()`
calls: those dispatch directly on a target with no real-coordinate
hit-testing, so they can't expose a "the button moved out from under the
touch" bug — reproducing it required measuring `getBoundingClientRect()`
before and after activation to catch the shift directly.

## The fix

Moved field activation from a `pointerdown` listener to a `click`
listener (both still delegated on `document`; `focusin` is unchanged for
keyboard navigation). This works because of a event-dispatch guarantee,
not a timing coincidence: for a single click, the target element's own
handler (the choice/toggle/counter button's `onclick`, which applies the
value) always runs during the target phase, strictly before the event
bubbles up to a `document`-level listener. So the value is committed
first, and the toolbar reveal — and the layout shift it causes — only
happens afterward, once the tap has already fully completed and there's
no pending hit-testing left for it to disrupt.

No other logic changed. `setActiveField()`'s single-active-field
enforcement, the choice/toggle/counter/multi handlers, and the toolbar
CSS are all exactly as before.

## Verified

- A single tap on a Property Type button, on a field that was not yet
  active, now sets the value immediately and shows `.selected` — checked
  against a freshly re-queried element, since the render triggered by the
  button's own click handler happens before the field is marked active.
- Measured zero layout shift on the tapped button between pointerdown
  and pointerup — the shift now happens strictly after, once the click
  has fully dispatched.
- A single tap on Occupancy → Vacant applies immediately and activates
  the field in the same tap.
- A counter `+` tap increments by exactly one, not two.
- Rapid switching across four different fields (text and choice types)
  correctly activates each one in turn, with exactly one field ever
  showing `.field.active` at a time.
- No regressions: Sketch, Footprint, Photos, dictation, tab badges/NEW
  indicators, the Rules engine, and PDF export all confirmed still
  working, including a live end-to-end check that Occupancy → Vacant
  still correctly reveals Mechanical's NEW-badged fields in one tap.

## Test checklist

1. Regenerate with `python generate.py`.
2. Open the app and confirm version 8.0.9.
3. Tap a Property Type button on an inactive field once — confirm
   immediate selection and toolbar reveal.
4. Tap Occupancy once — confirm immediate selection.
5. Tap a counter `+` once — confirm exactly one increment.
6. Toggle a Yes/No field once — confirm immediate response.
7. Switch between several fields quickly — confirm no control ever
   needs a second tap.
