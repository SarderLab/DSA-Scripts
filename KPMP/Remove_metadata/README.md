# Metadata Cleaner

`remove_metadata.py` deletes **all user metadata keys** (the key/value pairs shown under
*Metadata* on an item) from every item in a folder and all of its subfolders.

It does not touch the image files, annotations, or large-image metadata.

> ⚠️ **This cannot be undone, and there is no dry run.** Export the metadata first if you might need it
> (see [`Metadata`](https://github.com/SarderLab/DSA-Scripts/blob/main/KPMP/Metadata/Metadata.py)).

---

## Requirements

- Python 3.8+ and `girder-client` (`pip install girder-client`)
- An API key (see the [main README](../../README.md#3-get-an-api-key-or-use-your-usernamepassword))
- Write access to the items in the folder

---

## Step 1: Back up the metadata (recommended)

Export it with the scripts in [`Metadata`](https://github.com/SarderLab/DSA-Scripts/blob/main/KPMP/Metadata/Metadata.py), or
download it from the web interface.

## Step 2: Configure

Open `remove_metadata.py` and edit:

| Setting | What to put there |
|---|---|
| `GirderClient(apiUrl=...)` | `https://devathena.rc.ufl.edu/api/v1/` (testing) or `https://athena.rc.ufl.edu/api/v1/` (official) |
| `gc.authenticate(apiKey=...)` | Your API key. Remove it again before committing. |
| `folder_id` | The top-level folder ID ([how to find it](../../README.md#4-find-the-ids-the-scripts-ask-for)) |

**To delete only some keys** instead of all of them, change this line:

```python
keys = list(metadata.keys())
```

to a list of the keys you want removed, keeping only those that exist on the item:

```python
keys = [k for k in ["key_to_remove_1", "key_to_remove_2"] if k in metadata]
```

## Step 3: Run

```bash
cd DSA-Scripts/KPMP/remove_metadata
python remove_metadata.py
```

The script prints nothing while it works. It is finished when the command returns without an error.

## Step 4: Verify

Open a few items in the server's data browser and check that the **Metadata** section is empty,
or that only the intended keys were removed.
