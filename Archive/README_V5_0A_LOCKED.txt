Clipboard 5.0a Locked Sketch Build

Implemented locked workflow:
- Live-chain exterior measurement: segments remain provisional until Commit Chain.
- First wall uses absolute Up, Down, Left, or Right controls.
- Subsequent walls may use predefined relative turns before the line is added:
  90 Left/Right, 45 Left/Right, 22.5 Left/Right, Continue, or Custom.
- Decimal feet, feet/inches, and dash notation such as 24-6 are accepted.
- Separate Undo Live Segment and Undo Committed controls.
- Cancel Live Chain without changing committed geometry.
- Commit Chain saves all provisional segments together.
- Closure tolerance and estimated closure discrepancy remain available.
- Closed committed polygons calculate area; live segments never affect area.
- Multiple structures, floors, copied floors, open-to-below, reference lines,
  annotations, zoom, pan, and imported backgrounds remain available.

Basic test:
1. Open index.html or run Start_Clipboard_v4.bat.
2. Open Sketch.
3. Tap the grid to set a start point.
4. Enter 20 and tap Right.
5. Enter 5 and tap 90 Right.
6. Enter 3 and tap 90 Left.
7. Confirm the three lines remain blue/dashed and listed under LIVE CHAIN.
8. Tap Commit Chain. Lines should become solid and numbered.
