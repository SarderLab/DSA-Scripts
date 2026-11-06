# Athena → HiPerGator Metadata Export

Downloads user metadata (and optionally annotations, large-image metadata, and files)
from Athena or DevAthena to HiPerGator, then aggregates the metadata into a CSV.

Server URLs and credentials are read from `common.py`.

## Export metadata (on HiPerGator)

```bash
# by user or collection IDs (comma-separated)
sbatch Metadata.sh athena --UserOrCollection <IDs> --dest <path>

# by folder ID
sbatch Metadata.sh athena --folder <FolderID> --dest <path>
```

`--dest` is optional (default: the current directory). Use `devathena` instead of `athena` for the dev server.

## Download annotations / metadata / files for a folder

```bash
python annotations_user_large_metadata.py athena --folder <FolderID> --annotations          --dest <path>
python annotations_user_large_metadata.py athena --folder <FolderID> --user_metadata        --dest <path>
python annotations_user_large_metadata.py athena --folder <FolderID> --large_image_metadata --dest <path>
python annotations_user_large_metadata.py athena --folder <FolderID> --file                 --dest <path>
```

## Aggregate to CSV

```bash
python metadata_csv.py /path/to/json_files /path/to/output/metadata.csv
```

## Logs

Written to `logs/` in the destination folder:
- `error_log_UserMeta.txt`: errors
- `user_meta_data_log.txt`: items exported
- `tracking_data.json`: progress tracking
