# gdrive_auth.py 
import os
import json
import streamlit as st  # used to read st.secrets when running on Streamlit Cloud
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# Use broad drive scope so we can create folders/files and permission changes
SCOPES = ["https://www.googleapis.com/auth/drive"]

def _get_service_account_info_from_secrets():
    """
    Returns service account info dict (parsed JSON) if st.secrets contains SERVICE_ACCOUNT_JSON.
    """
    try:
        sa_json = st.secrets.get("SERVICE_ACCOUNT_JSON", None)
    except Exception:
        sa_json = None
    if sa_json:
        if isinstance(sa_json, str):
            return json.loads(sa_json)
        return sa_json
    return None

def get_drive_service():
    """
    Returns an authenticated Drive v3 service using a Service Account.
    Fallbacks:
      1) st.secrets['SERVICE_ACCOUNT_JSON'] (Streamlit Cloud)
      2) GOOGLE_APPLICATION_CREDENTIALS env var path to the JSON file
    Raises RuntimeError if neither is available.
    """
    # Attempt 1: Streamlit secrets (cloud)
    sa_info = _get_service_account_info_from_secrets()
    if sa_info:
        creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    # Attempt 2: environment file path
    gpath = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gpath and os.path.exists(gpath):
        creds = service_account.Credentials.from_service_account_file(gpath, scopes=SCOPES)
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    raise RuntimeError("Service account credentials not found. Add SERVICE_ACCOUNT_JSON to Streamlit secrets or set GOOGLE_APPLICATION_CREDENTIALS env var.")

def set_public_permission(service, file_id):
    """
    Make a file viewable by anyone with link. Use with caution.
    """
    try:
        permission_body = {"role": "reader", "type": "anyone"}
        service.permissions().create(fileId=file_id, body=permission_body).execute()
    except HttpError as e:
        # permission could already exist or be blocked
        raise
