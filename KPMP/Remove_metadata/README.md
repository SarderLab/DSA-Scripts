# Metadata Cleaner

Deletes **all** user metadata keys from every item in a folder and its subfolders.

## Usage

1. Set `folder_id` and your API key in the script.
   To delete only some keys, edit the `keys` list before the API call.
2. Run:
   ```bash
   python remove_metadata.py
   ```

⚠️ This cannot be undone and there is no dry run. Export the metadata first if you might need it
(see [`Metadata`]((https://github.com/SarderLab/DSA-Scripts/blob/main/KPMP/Metadata/Metadata.py))).
