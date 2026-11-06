# Annotation Access Cleaner

`annotation_access_control.py` removes specific users from the access list of every annotation layer
in a folder (and all its subfolders), **except** layers whose names are in `keep_names`.

Result: the listed users can no longer see the other layers. They still see the kept layers.

- Only the users in `user_ids` are affected. Other users, groups, and admins are not changed.
- Changed layers also get `public` turned off.
- Nothing is deleted.

> ⚠️ There is **no dry run and no backup**. Changes happen immediately.
> For a safer workflow with dry run, backups, and undo, use
> [`annotation_namechange_accesscontrol`](https://github.com/SarderLab/DSA-Scripts/blob/main/KPMP/annotation_namechange_accesscontrol/annotation_namechange_accesscontrol.py).

---

## Requirements

- Python 3.8+ and `girder-client` (`pip install girder-client`)
- An API key (see the [main README](../../README.md#3-get-an-api-key-or-use-your-usernamepassword))
- Admin rights on the annotations you want to change

---

## Step 1: Configure

Open `annotation_access_control.py` and edit:

| Setting | What to put there |
|---|---|
| `GirderClient(apiUrl=...)` | `https://devathena.rc.ufl.edu/api/v1/` (testing) or `https://athena.rc.ufl.edu/api/v1/` (official) |
| `gc.authenticate(apiKey=...)` | Your API key. Remove it again before committing. |
| `user_ids` | User IDs to remove, e.g. `{'64430aac435c92704a300268', '...'}` |
| `folder_id` | The top-level folder ID |
| `keep_names` | Layer names the users should keep seeing. They must match **exactly**. |



**Do not put your own user ID in `user_ids`**, or you may lose access to the layers yourself.

---

## Step 2: Run

```bash
cd DSA-Scripts/KPMP/annotation_access_control
python annotation_access_control.py
```

As it runs, the script prints:
- `skipping <name>` for kept layers
- the access list of each other layer
- `Removing listed users from: <name>` when a change is made
- `Completed <folder>` after each subfolder, then `completed`

---

## Step 3: Verify

Log in to HistomicsUI as one of the users in `user_ids` (or ask them to), open a few slides,
and confirm only the `keep_names` layers are visible.

---

## Notes

- If a user can see a layer through a **group**, removing them from the user list does not hide it.
  Group access must be changed separately.
- To undo, add the users back to the layers' access lists in the web interface.
  It is easier to test on DevAthena first.
