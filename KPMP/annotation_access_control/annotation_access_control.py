import os
import json
from girder_client import GirderClient

gc = GirderClient(apiUrl='https://athena.rc.ufl.edu/api/v1/')
#Add your API key
gc.authenticate(apiKey='YOUR-API-KEY')

#update this as needed (it can take multiple comma separated ID's)
user_ids= {'64430aac435c92704a300268'}

#update this as needed
folder_id = '69e6919a3c7545c729a39e88'

#update this as needed
keep_names = {
    "non_globally_sclerotic_glomeruli",
    "globally_sclerotic_glomeruli",
    "tubules",
    "peritubular_capillaries",
    "arteries/arterioles"
    }

def hide_annotations_recursive(gc, folder_id):
    items = gc.listItem(folder_id)

    for item in items:
        metadata = item.get('meta', {}) 
        item_id = item['_id']
        
        annotations = gc.get(
            "annotation",
            parameters={"itemId": item_id, "limit": 0}
        )

        for ann in annotations:
            ann_id = ann["_id"]
            name = ann["annotation"].get("name", "")
            name = name.strip()

            if name in keep_names:
                print(f"skipping {name}")
                continue

            #  get list of accesses (this is the key step)
            full_access = gc.get(f"annotation/{ann_id}/access")
            # print(full_access)

            users = full_access.get("users", [])
            print(f"users:{users}")
            groups = full_access.get("groups", [])
            # print(f"groups: {groups}")

            # remove users from access list json
            new_users = [
                u for u in users
                if u["id"] not in user_ids
            ]
            print(new_users)

            # only update if needed
            if len(new_users) != len(users):
                print(f"Removing listed users from: {name}")

                gc.put(
                    f"annotation/{ann_id}/access",
                    parameters={
                        "access": json.dumps({
                            "users": new_users,
                            "groups": groups
                        }),
                        "public": "false"
                    }
                )

    subfolders = gc.listFolder(folder_id, parentFolderType='folder')

    for folder in subfolders:
        clear_metadata_recursive(gc, folder['_id'])
        print(f"Completed {folder['name']}")
        
hide_annotations_recursive(gc, folder_id)
print("completed")

