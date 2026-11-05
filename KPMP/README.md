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

### Annotations access control
- The file `annotation_access_control.py` will help you understand how you can change someone's access control to the annotations on Athena.
- The file `annotation_namechaneg_accesscontrol.py` is easy also addressing the same access control of annotations but it also helps change the names of the annotations.
- As admin you can always view the annotations irrespective of the hidden/visible status.
