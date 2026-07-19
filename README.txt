Clipboard v4

WINDOWS
1. Keep Clipboard_v4_Master_Base.xlsx in this folder.
2. Double-click Start_Clipboard_v4.bat.
3. The batch file runs generate.py, rebuilds clipboard_generated/config.json from the workbook, and opens http://localhost:8000.
4. Keep the command window open while using Clipboard.

MAC
Double-click start_clipboard_v4.command. You may need to allow it in Privacy & Security the first time.

IMPORTANT
- The workbook is now the live source of truth.
- Save workbook changes before starting Clipboard.
- Each launch regenerates config.json from the workbook.
- App data is stored locally in the browser under the Clipboard v4 storage key.
- Photos are represented by metadata in this prototype.
- Sketch remains a placeholder.

Version 4.1 visibility fix:
- Applies workbook default values even when older browser data exists.
- Supports =, ==, !=, <>, >, <, >=, <=, AND, and OR visibility rules.
- Re-evaluates visibility immediately when dropdowns or other fields change.
- Clears values for fields that become hidden.
