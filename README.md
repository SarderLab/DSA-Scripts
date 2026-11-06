# DSA-Scripts

Python scripts for managing whole-slide images, annotations, and metadata on the
Digital Slide Archive (DSA / HistomicsUI) servers Athena and DevAthena, using the Girder API (`girder-client`).

## Contents

| Folder | What it does |
|---|---|
| [`KPMP/annotation_access_control`](KPMP/annotation_access_control.py) | Bulk-rename annotation layers and set which layers non-admin users can see |
| [`KPMP/annotation_access_control`](KPMP/annotation_access_control) | Remove specific users from annotation access lists, except for kept layers |
| [`KPMP/remove_metadata`](KPMP/remove_metadata) | Delete all user metadata from items in a folder |
| [`KPMP/athena_to_hipergator_metadata`](KPMP/athena_to_hipergator_metadata) | Export user metadata and annotations from Athena to HiPerGator, and aggregate them to CSV |

## Requirements

```bash
pip install girder-client pandas
```

## General notes

- All scripts process the given folder **and its subfolders**.
- Log in with your own API key (DSA → *My account* → *API keys*) or your username and password.
- **Never commit API keys.** Test on DevAthena before running on Athena.
- Changes to access or metadata need the right permissions on the server (admin for access control).
