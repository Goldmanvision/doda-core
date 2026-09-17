# DoDA Content Workbench

This folder contains the CLI-first content authoring, validation, export, and
eventual desktop GUI tooling for DoDA.

## Source-of-truth policy

- `data_authoring/source/` contains editable CSV source data.
- `data_authoring/schemas/` contains schemas and controlled-value definitions.
- `generated/` contains rebuildable machine-generated outputs.
- `build/` contains generated PK3 artifacts.
- Do not manually edit `generated/` or `build/` outputs.

## Initial commands

Activate the environment:

```powershell
& .\tools\doda_content_workbench\.venv\Scripts\Activate.ps1
```

Run the future command-line tool:

```powershell
python -m doda_workbench --help
```
