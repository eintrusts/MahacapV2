# state_drive.py (NEW file)
import json
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from gdrive_auth import get_drive_service

def _escape(s: str) -> str:
    return s.replace("'", "\\'")

def save_state_json_to_folder(folder_id, state_dict, filename="state.json"):
    service = get_drive_service()
    # Delete existing state.json in folder (optional)
    q = f"name = '{_escape(filename)}' and '{folder_id}' in parents and trashed = false"
    existing = service.files().list(q=q, spaces='drive', fields='files(id,name)').execute().get('files', [])
    for f in existing:
        try:
            service.files().delete(fileId=f['id']).execute()
        except Exception:
            pass

    bytes_io = BytesIO()
    bytes_io.write(json.dumps(state_dict, ensure_ascii=False, indent=2).encode('utf-8'))
    bytes_io.seek(0)
    media = MediaIoBaseUpload(bytes_io, mimetype='application/json', resumable=False)
    meta = {'name': filename, 'parents': [folder_id]}
    created = service.files().create(body=meta, media_body=media, fields='id').execute()
    return created

def load_state_json_from_folder(folder_id, filename='state.json'):
    service = get_drive_service()
    q = f"name = '{_escape(filename)}' and '{folder_id}' in parents and trashed = false"
    resp = service.files().list(q=q, spaces='drive', fields='files(id,name)', pageSize=1).execute()
    files = resp.get('files', [])
    if not files:
        return None
    file_id = files[0]['id']
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, service.files().get_media(fileId=file_id))
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    try:
        return json.load(fh)
    except Exception:
        return None
