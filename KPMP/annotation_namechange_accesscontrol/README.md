# Annotation Rename & Access Control

`annotation_namechange_accesscontrol.py` processes every slide in one or more folders
(including all subfolders) and does three things:

1. **Renames annotation layers** using `RENAME_MAP` (exact old name → new name).
2. **Controls visibility** for logged-in **non-admin** users:
   - Renamed layers and layers in `PROTECTED_NAMES` are made visible (read access for everyone
     who can open the slide). Nobody's existing access is reduced.
   - Every other layer is hidden: all non-admin users and groups are removed, and public is turned off.
   - Site admins always see everything.
3. **Handles duplicates:** if a slide has 2+ layers with the same final name, the one with the most
   shapes stays visible and the others are hidden.

It **never deletes** anything and **never changes shapes**. It has a dry run, backups, and an undo.

---

## Requirements

- Python 3.8+ and `girder-client` (`pip install girder-client`)
- An account with **admin rights on the annotations** you want to change. A site admin account is best.
  Without admin rights, access changes fail and are listed as errors in the report.

---

## Step 1: Configure the script

Open `annotation_namechange_accesscontrol.py` and edit the settings at the top:

| Setting | What to put there |
|---|---|
| `API_URL` | `https://devathena.rc.ufl.edu/api/v1/` for testing, `https://athena.rc.ufl.edu/api/v1/` for the official server |
| `FOLDER_IDS` | List of top-level folder IDs, e.g. `["659eb5acbd96faac30eb2350", "..."]`. Subfolders are included automatically. |
| `RENAME_MAP` | `"old name": "new name"` pairs. Old names must match **exactly** (case, underscores, slashes). |
| `PROTECTED_NAMES` | Layers that must **never be renamed**, e.g. `{"IFS", "cortical heatmap", "medullary heatmap"}` |
| `PROTECTED_VISIBLE` | `True` = protected layers are visible to non-admins. `False` = they are hidden. |
| `DUPLICATE_MODE` | `"hide"` = hide extra copies. `"report"` = only list them. |
| `DRY_RUN` | Leave as `True` for the first run. |
| `WORKERS` | Slides processed in parallel. 8–16 is fine. Don't go higher on the shared server. |
| `MAX_SLIDES` | Set e.g. `20` to try only a few slides first. `None` = all slides. |
| `VERBOSE` | `False` (recommended). `True` prints a line for every change, which slows notebooks down. |



---

## Step 2: Log in

Choose one:

- **Username and password (simplest):** do nothing. The script asks for them when it starts.
  The password is hidden while you type.
- **API key:** set it as an environment variable before running:
  ```bash
  export ATHENA_API_KEY="paste-your-key-here"
  ```

Never write the key into the script file.

---

## Step 3: Dry run (changes nothing)

From a terminal:

```bash
cd DSA-Scripts/KPMP/annotation_namechange_accesscontrol
python annotation_namechange_accesscontrol.py
```

In Jupyter, paste the **whole script into a single cell** and run it.

The script prints:
- who you are logged in as and whether you are a **site admin**
- the names of the folders it will process (check that they are correct)
- progress, e.g. `150/456 slides done, 3.1 min so far, ~6.2 min left`
- a **report** with:
  - totals: slides, renames, access changes, errors
  - every layer name found, labelled `VISIBLE`, `protected`, `hidden`, or `LOOK-ALIKE`
  - slides missing one of the expected layers
  - duplicates
  - **look-alike names**: layers that resemble a rename target but are spelled differently
    (e.g. `GLOBALLY_sclerotic_glomeruli`). These are not touched. Add them to `RENAME_MAP` if they should be renamed.
  - errors

A full list of planned changes is saved to `runs/<timestamp>_dryrun/plan.csv`.

**Check before continuing:**
- `errors: 0`. Errors usually mean missing permissions; see Troubleshooting.
- The `VISIBLE` and `protected` names are exactly the layers you want people to see.
- There are no unexpected look-alikes.

---

## Step 4: Live run

1. Set `DRY_RUN = False`.
2. Run the script again.
3. When asked `Type YES to continue`, type `YES` (capital letters).

Before each change, the script saves a backup to `runs/<timestamp>/`, and it writes every change to
`runs/<timestamp>/changes.csv`. The last line of the report shows the folder name. **Write it down.**

---

## Step 5: Verify

1. Set `DRY_RUN = True` and run again. The report should show `renames: 0` and `access changes: 0`.
2. Log in to HistomicsUI as a **normal (non-admin) user** and open a few slides.
   Only the expected layers should appear.
   Admins see every layer, so checking as an admin proves nothing.

---

## Undo a live run

1. Set `RESTORE_RUN = "runs/<timestamp>"`, using the folder from the live run.
2. Set `DRY_RUN = True` and run to preview, then set `DRY_RUN = False` and run to restore.

Names and access lists go back exactly as they were. Shapes added since then are kept.

---

## Re-running

Re-running is safe. It only changes what is still not correct, so if a run is interrupted, just run it again.

---

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `HTTP error 401 ... (user None)` | Not logged in. Run the whole script from the top. In Jupyter, keep the whole script in one cell. |
| `HTTP error 403 ... access denied` | Your account lacks admin rights on those annotations. Ask a DSA administrator to grant them or run the script. |
| `site admin: False` warning | You are not a site admin. You stay on hidden layers so you can fix them, so **you** will still see them. |
| A layer you expected to rename is listed as `hidden` | The old name in `RENAME_MAP` doesn't match exactly. Copy the name from the report. |
| Very slow | Keep `VERBOSE = False`. Raise `WORKERS` up to 16. A live run is slower than a dry run because renaming re-uploads each layer. |
