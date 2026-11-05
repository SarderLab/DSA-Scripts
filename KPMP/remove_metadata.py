import os
import json
from girder_client import GirderClient

gc = GirderClient(apiUrl='https://athena.rc.ufl.edu/api/v1/')
#Add your API key
gc.authenticate(apiKey='YOUR-API-KEY')

#update this as needed
folder_id = '69e6919a3c7545c729a39e88'

def clear_metadata_recursive(gc, folder_id):
    items = gc.listItem(folder_id)

    for item in items:
        metadata = item.get('meta', {}) 
        if metadata:
            keys = list(metadata.keys())

            gc.sendRestRequest(
                method='DELETE',
                path=f'item/{item["_id"]}/metadata',
                data=json.dumps(keys),
                headers={'Content-Type': 'application/json'}
            )

    subfolders = gc.listFolder(folder_id, parentFolderType='folder')

    for folder in subfolders:
        clear_metadata_recursive(gc, folder['_id'])
        
clear_metadata_recursive(gc, folder_id)