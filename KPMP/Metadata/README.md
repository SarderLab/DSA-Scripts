# Athena → HiPerGator Metadata Export

Scripts to copy data from Athena or DevAthena to HiPerGator and combine metadata into a CSV.

| File | Purpose |
|---|---|
| `Metadata.py` | Downloads **user metadata** of every item (by folder, user, or collection) as one JSON file per item |
| `Metadata.sh` | SLURM job script that runs `Metadata.py` on HiPerGator |
| `annotations_user_large_metadata.py` | Downloads annotations, user metadata, large-image metadata, or files for a folder |
| `metadata_csv.py` | Combines the downloaded JSON metadata files into one CSV |
| `common.py` | Holds the server URLs and credentials used by the scripts above |

Nothing on the server is changed. These scripts only read.

---

## Requirements

- A HiPerGator account with SLURM access, or any machine with Python 3.8+
- Python packages: `pip install --user girder-client pandas`
- An API key for the server (see the [main README](../../README.md#3-get-an-api-key-or-use-your-usernamepassword))

---

## Step 1: Copy the files to HiPerGator

Copy this whole folder to your HiPerGator directory, for example:

```bash
scp -r athena_to_hipergator_metadata <gatorlink>@hpg.rc.ufl.edu:/blue/<group>/<gatorlink>/
```

## Step 2: Set credentials in `common.py`

The scripts call `common.urlAndCredentials("<instance>")` to get the API URL, API key, and cookie
for `athena` or `devathena`. Open `common.py` and fill in your API key for the instance you will use.

Do not commit `common.py` with a real key in it.

## Step 3: Export user metadata

Run these from the folder that contains the scripts.

**By folder** (comma-separate several IDs):

```bash
sbatch Metadata.sh athena --folder <FolderID> --dest <destination_path>
```

**By user or collection** (comma-separate several IDs):

```bash
sbatch Metadata.sh athena --UserOrCollection <UserOrCollectionIDs> --dest <destination_path>
```

- Replace `athena` with `devathena` to use the dev server.
- `--dest` is optional. Without it, output goes to the folder you run the command from.

Example:

```bash
sbatch Metadata.sh athena --folder 66b667e31acc7e45f89554a2 --dest /blue/<group>/<gatorlink>/metadata_out
```

Check the job with `squeue -u <gatorlink>`. Output is printed to the SLURM `.out` file.

**Output:**

```
<dest>/
├── <FolderName>/UserMetaData/<slide_name>.json      # by --folder
├── <user_or_collection>/.../UserMetaData/*.json     # by --UserOrCollection (server folder structure is kept)
└── logs/
    ├── error_log_UserMeta.txt      # errors
    ├── user_meta_data_log.txt      # every item exported
    └── tracking_data.json          # items processed so far
```

Only items that have user metadata get a JSON file.

## Step 4 (optional): Download annotations, large-image metadata, or files

```bash
python annotations_user_large_metadata.py athena --folder <FolderID> --annotations          --dest <path>
python annotations_user_large_metadata.py athena --folder <FolderID> --user_metadata        --dest <path>
python annotations_user_large_metadata.py athena --folder <FolderID> --large_image_metadata --dest <path>
python annotations_user_large_metadata.py athena --folder <FolderID> --file                 --dest <path>
```

## Step 5: Combine metadata into a CSV

```bash
python metadata_csv.py <folder_with_json_files> <output_csv_path>
```

Example:

```bash
python metadata_csv.py /blue/<group>/<gatorlink>/metadata_out/<FolderName>/UserMetaData /blue/<group>/<gatorlink>/metadata.csv
```

Each JSON file becomes one row in the CSV. Files that can't be read are reported and skipped.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Error during GirderClient initialization or authentication` | Check the API key and URL in `common.py`. |
| `HTTP error 401` / `403` | Your account can't read that folder, user, or collection. Ask for access. |
| No JSON files created | The items have no user metadata. Check one item in the web interface. |
| `ModuleNotFoundError: common` | Run the command from the folder that contains `common.py`. |
