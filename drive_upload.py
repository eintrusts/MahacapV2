from googleapiclient.http import MediaFileUpload
from gdrive_auth import get_drive_service

def get_or_create_folder(city_name):
    service = get_drive_service()
    # Check if folder exists
    results = service.files().list(
        q=f"name='{city_name}' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    # Create folder
    file_metadata = {
        'name': city_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_file_to_folder(file_path, folder_id):
    service = get_drive_service()
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')
