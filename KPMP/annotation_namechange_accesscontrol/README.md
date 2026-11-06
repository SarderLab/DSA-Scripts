# Annotation Rename & Access Control

Renames annotation layers and sets their visibility on every slide in the given folders.

- Renames layers listed in `RENAME_MAP`.
- Non-admin users see only the renamed layers and `PROTECTED_NAMES`. All other layers are hidden.
- Nothing is deleted. Shapes are never changed.

## Usage

```bash
python annotation_namechange_accesscontrol.py
```

1. Set `API_URL` and `FOLDER_IDS` at the top of the script.
2. Run with `DRY_RUN = True` (default) and review the report and `plan.csv`.
3. Set `DRY_RUN = False`, run, and type `YES`.
4. To undo, set `RESTORE_RUN = "runs/<timestamp>"` and run again.

Requires admin rights on the annotations. Do not commit the `runs/` folder (it contains backups of access lists).
