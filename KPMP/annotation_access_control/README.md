# Annotation Access Cleaner

Removes specific users from the access lists of every annotation in a folder,
except for annotations whose names are in `keep_names`.

## Usage

1. Set `user_ids`, `folder_id`, `keep_names`, and your API key in the script.
2. Run:
   ```bash
   python annotation_access_control.py
   ```

Note: this changes access immediately; there is no dry run. For renaming layers and a safer workflow with dry run and undo,
see [`annotation_namechange_accesscontrol`](KPMP/annotation_namechange_accesscontrol).
