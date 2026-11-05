# Annotation Access Cleaner (Girder)

This script connects to a Girder instance and recursively removes specific users from annotation access lists while preserving selected annotation types.

---

## Overview

The script:

- Authenticates with a Girder API using an API key  
- Iterates through all items in a specified folder  
- Retrieves annotations for each item  
- Skips annotations with names in a predefined keep list  
- Removes specified users from annotation access control lists  
- Recursively processes subfolders  

---

## Requirements

- Python 3.x  
- `girder-client`

Install dependencies:

```bash
pip install girder-client
```

## How to run script
- Update the users list, folder id, annotation names, and API Key
- Run the script `python annotation_access_control.py`

<br>
<br>
<br>

# Girder Metadata Cleaner (Recursive)

This script recursively removes metadata from all items inside a specified Girder folder and its subfolders.

---

## Overview

The script:

- Connects to a Girder instance using an API key  
- Traverses a folder recursively  
- Finds all items in each folder  
- Deletes all metadata keys from each item  
- Processes subfolders automatically  

---

## How to run script
- Update the folder id, and API Key (changes the json as needed before calling the API **if you want controlled cleaning**)
- Run the script `python remove_metadata.py`

# Annotation Rename & Access Control (HistomicsUI / DSA)

Bulk-renames annotation layers and sets their visibility across all slides in the
given folders (subfolders included), using `girder_client`.

- Renames layers listed in `RENAME_MAP`.
- Non-admin users see only the renamed layers and `PROTECTED_NAMES`. All other layers are hidden.
- Nothing is deleted. Shapes are never changed.

## Usage

```bash
pip install girder-client
python annotation_namechange_accesscontrol.py
```

1. Set `API_URL` and `FOLDER_IDS` at the top of the script.
2. Run with `DRY_RUN = True` (default) and review the report and `plan.csv`.
3. Set `DRY_RUN = False`, run, and type `YES`.
4. To undo, set `RESTORE_RUN = "runs/<timestamp>"` and run again.

Requires admin rights on the annotations. Do not commit API keys or the `runs/` folder.
