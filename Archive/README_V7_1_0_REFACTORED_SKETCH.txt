Clipboard v7.1.0 - Refactored Field Sketch

Focus: iPad Mini 6 input stability and editable sketch objects.

Implemented:
- Pointer Events input engine
- Coalesced Apple Pencil samples
- Continuous pencil, line, arrow and circle drawing
- Two-finger pan and pinch zoom
- Object selection, movement and corner resizing
- Editable text labels, dimensions and notes
- Duplicate and delete selected objects
- Larger high-contrast outdoor tool buttons
- Object-based save/load with migration from v7 strokes

Acceptance test:
1. Draw continuously for 60 seconds with Pencil.
2. Pinch zoom and two-finger pan in each tool mode.
3. Select, move and resize a line, arrow, circle and text object.
4. Edit text and verify save after reopening.
