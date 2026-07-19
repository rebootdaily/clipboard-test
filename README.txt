Clipboard v4.3.2 Clean Build

SOURCE OF TRUTH
- Clipboard_v4_Master_Base.xlsx: inspection form configuration
- app_template/app.js: application logic
- app_template/index.html: application layout and styles
- app_template/manifest.json: installable web app metadata
- generate.py: builds config.json and publishes the app

GENERATE AND TEST
Windows: double-click Start_Clipboard_v4.bat
macOS: run start_clipboard_v4.command

The generator recreates clipboard_generated and publishes these files to the project root for GitHub Pages:
- app.js
- config.json
- index.html
- manifest.json

Do not edit files in clipboard_generated or the published root copies. Edit only the workbook, generate.py, or app_template files, then rebuild.

v4.3.2 fixes
- Text, currency, date, time, and long-text fields no longer lose focus while typing.
- Counter bar remains hidden outside Interior, Sketch, Exit Interview, and Review.
- Obsolete versioned JavaScript files are removed during publishing.
