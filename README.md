# KPMP
## Annotation Access Cleaner (Girder)

This script connects to a Girder instance and recursively removes specific users from annotation access lists while preserving selected annotation types.

---

### Overview

The script:

- Authenticates with a Girder API using an API key  
- Iterates through all items in a specified folder  
- Retrieves annotations for each item  
- Skips annotations with names in a predefined keep list  
- Removes specified users from annotation access control lists  
- Recursively processes subfolders  

---

### Requirements

- Python 3.x  
- `girder-client`

Install dependencies:

```bash
pip install girder-client
```

### How to run script
- Update the users list, folder id, annotation names, and API Key
- Run the script `python annotation_access_control.py`

<br>
<br>
<br>

## Girder Metadata Cleaner (Recursive)

This script recursively removes metadata from all items inside a specified Girder folder and its subfolders.

---

### Overview

The script:

- Connects to a Girder instance using an API key  
- Traverses a folder recursively  
- Finds all items in each folder  
- Deletes all metadata keys from each item  
- Processes subfolders automatically  

---

### How to run script
- Update the folder id, and API Key (changes the json as needed before calling the API **if you want controlled cleaning**)
- Run the script `python remove_metadata.py`

## Annotation Rename & Access Control (HistomicsUI / DSA)

Bulk-renames annotation layers and sets their visibility across all slides in the
given folders (subfolders included), using `girder_client`.

- Renames layers listed in `RENAME_MAP`.
- Non-admin users see only the renamed layers and `PROTECTED_NAMES`. All other layers are hidden.
- Nothing is deleted. Shapes are never changed.

### Usage

```bash
pip install girder-client
python annotation_namechange_accesscontrol.py
```

1. Set `API_URL` and `FOLDER_IDS` at the top of the script.
2. Run with `DRY_RUN = True` (default) and review the report and `plan.csv`.
3. Set `DRY_RUN = False`, run, and type `YES`.
4. To undo, set `RESTORE_RUN = "runs/<timestamp>"` and run again.

Requires admin rights on the annotations. Do not commit API keys or the `runs/` folder.


## Athena To HiPerGator Metadata-CSV (Automation)

### Description
The file "Metadata.py" helps in automating the transfer of usermetada from anthena to HiPerGator. "Metadata.py" which when executed transfers all the user metadata content from athena/devathena to HiPerGator. 

It uses the girder-client which is a python client library and a CLI to allow for programatic interaction with Girder server, and also to workaround limitations of the web client.

The Metadata file focuses on the detailed, often supplementary data elements essential for a complete dataset representation. Folders containing user metadata are created in locations with items. These folders are organized alongside the items they correspond to.

Note: All "Athena" folders are generated in the same directory as the execution absolute path. This means that the directory structure for these folders is maintained as defined in their initial configuration, ensuring a consistent and predictable file organization.

#### Installation
Assuming these files are transferred into HiPerGator.

To start transfer of user metadata from User or Collection to HiPerGator
```
sbatch Metadata.sh athena --UserOrCollection userIDs/CollectionIDs --dest dest_addr(optional)
```

To start transfer of specific folder's user metadata to HiPerGator
```
sbatch Metadata.sh athena --folder FolderID --dest dest_addr(optional)
```

NOTE: If destination address is not specified the destination will be the same folder as you are running the code.


Example command to run in HiPerGator
```
sbatch Metadata.sh athena --folder 66b667e31acc7e45f89554a2 --dest /home/blue/pinaki.sarder/nikhil.yerra/test
```

##### JSON to CSV Metadata Extraction Script
Once the required metadata is transferred to the hipergator, use the metadata_csv.py file to aggregate this metadata to a csv file.
This Python script processes JSON files in a specified directory, extracting into a DataFrame, and then saves the collected data to a CSV file. It handles errors gracefully and provides feedback on its progress and any issues encountered.

### Requirements

- Python 3.x
- `pandas` library (can be installed via `pip install pandas`)

### Usage

To run the script, use:
```
python metadata_csv.py /path/to/json_files /path/to/output/metadata.csv
```

#### logs
All logs are generated in a folder logs. These are generated whenever we run "Metadata.py". 

Error logs: <br/>
    [Metadata] error_log_UserMeta.txt <br/>

Audit logs: <br/>
    [Metadata] user_meta_data_log.txt <br/>


#### Commnad to run 
To download annotations of a specific folder

```
python annotations_user_large_metadata.py athena --folder <Folder ID> --annotations --dest /path/to/destination
```

To download user metadata of a specific folder

```
python annotations_user_large_metadata.py athena --folder <Folder ID> --user_metadata --dest /path/to/destination
```
To download user large image metadata of a specific folder

```
python annotations_user_large_metadata.py athena --folder <Folder ID> --large_image_metadata --dest /path/to/destination
```

To download only files of a specific folder

```
python annotations_user_large_metadata.py athena --folder <Folder ID> --file --dest /path/to/destination
```
