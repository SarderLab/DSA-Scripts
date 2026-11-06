# DSA-Scripts

Python scripts for bulk-managing slides, annotations, and metadata on the
Digital Slide Archive (DSA / HistomicsUI) servers:

| Server | API URL |
|---|---|
| Athena (official) | `https://athena.rc.ufl.edu/api/v1/` |
| DevAthena (testing) | `https://devathena.rc.ufl.edu/api/v1/` |

All scripts talk to the server through the Girder REST API using the `girder-client` Python package.

---

## Scripts

| Folder | Script(s) | Purpose |
|---|---|---|
| [`KPMP/annotation_namechange_accesscontrol`](KPMP/annotation_namechange_accesscontrol/annotation_namechange_accesscontrol.py) | `annotation_namechange_accesscontrol.py` | Rename annotation layers and control which layers non-admin users can see (dry run, backups, undo) |
| [`KPMP/annotation_access_control`](KPMP/annotation_access_control/annotation_access_control.py) | `annotation_access_control.py` | Remove specific users from annotation access lists, except for kept layers |
| [`KPMP/remove_metadata`](KPMP/Remove_metadata/remove_metadata.py) | `remove_metadata.py` | Delete user metadata from every item in a folder |
| [`KPMP/Metadata`](KPMP/Metadata)| `Metadata.py`, `Metadata.sh`, `metadata_csv.py`, `annotations_user_large_metadata.py`, `common.py` | Export metadata, annotations, and files from Athena to HiPerGator and combine metadata into a CSV |

Each folder has its own README with full instructions.

---

## One-time setup (needed for every script)

### 1. Install Python and the client library

Python 3.8 or newer is required. Check with:

```bash
python --version
```

Install the dependencies:

```bash
pip install girder-client pandas
```

On HiPerGator or a shared system without admin rights, use `pip install --user girder-client pandas`.

### 2. Get the code

```bash
git clone <this-repo-url>
cd DSA-Scripts/KPMP
```

### 3. Get an API key (or use your username/password)

1. Log in to the server in your browser (Athena or DevAthena).
2. Click your name in the top-right corner, then **My account**.
3. Open the **API keys** tab and click **Create new key**.
4. Give it a name and choose **Allow all actions**, then copy the key.

Treat the key like a password. **Never paste it into a file you commit to GitHub.**
`annotation_namechange_accesscontrol.py` can also log in with your username and password instead of a key.

### 4. Find the IDs the scripts ask for

Every object on the server has a 24-character ID (e.g. `69e6919a3c7545c729a39e88`).

| You need | Where to find it |
|---|---|
| **Folder ID** | Open the folder in the server's data browser. The ID is the last part of the URL after `folder/`. You can also click the folder's **ⓘ (info)** icon. |
| **Item (slide) ID** | Open the slide in HistomicsUI. The ID is the part of the URL after `?image=`. |
| **User ID** | In the data browser, open **Users** and click the person. The ID is the part of the URL after `user/`. |

---

## Ground rules

- **Test on DevAthena first**, then run on Athena.
- Scripts that change things need the right permissions. Changing access requires admin rights on the
  annotations (ideally a site admin account). Deleting metadata requires write access to the items.
- All scripts process the given folder **and all of its subfolders**.
- Keep `runs/` and `logs/` out of Git (already listed in `.gitignore`), because they contain user IDs and backups.
