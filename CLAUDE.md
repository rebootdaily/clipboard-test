# Clipboard Development Rules

Standing project instructions. These apply to every session working in this
repository and take precedence over general defaults.

1. The Excel workbook (`Clipboard_v4_Master_Base.xlsx`) is the source of truth.
2. Never modify, normalize, optimize, or restore workbook contents unless the
   user explicitly requests workbook edits.
3. Assume every workbook change is intentional, even if it looks inconsistent
   or incomplete (a hidden field, an unusual Visibility Rule, an apparently
   orphaned Follow-Up trigger, etc.).
4. If an inconsistency is detected, report it — do not fix it.
5. Only modify the generator (`generate.py`) or application code
   (`app_template/`) when requested.
6. Never overwrite the workbook from Git or a previous version (e.g. no
   `git checkout`/`git restore` on `Clipboard_v4_Master_Base.xlsx`, no
   restoring from a backup) unless explicitly asked to.
7. Before committing, summarize exactly which files will be changed.

For the deeper architecture behind these rules — why the workbook and
`app_template/` are separate sources of truth, what's generated vs.
hand-maintained, and the full development/release workflow — see
[Documentation/ARCHITECTURE.md](Documentation/ARCHITECTURE.md) and
[Documentation/CONTRIBUTING.md](Documentation/CONTRIBUTING.md).
