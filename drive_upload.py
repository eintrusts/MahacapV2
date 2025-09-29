# drive_upload.py  
import os
from googleapiclient.http import MediaFileUpload
from gdrive_auth import get_drive_service, set_public_permission

def get_or_create_folder(city_name, parent_id=None):
    """
    Find existing folder named city_name (under parent if given), else create it.
    Returns folder_id.
    """
    service = get_drive_service()
    # Prepare query - restrict to parent if provided
    q = f"name = '{city_name.replace(\"'\",\"\\\\'\")}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"

    results = service.files().list(q=q, spaces='drive', fields='files(id,name)').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']

    file_metadata = {'name': city_name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_file_to_folder(file_path, folder_id, make_public=False):
    """
    Upload a local file to Drive folder. Returns the created file resource (dict).
    """
    service = get_drive_service()
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink,webContentLink').execute()

    if make_public:
        try:
            set_public_permission(service, file.get('id'))
        except Exception:
            # warn but continue
            pass

    # return file metadata
    return file
