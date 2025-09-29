# gdrive_auth.py
import os
import json
import base64
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]

def _get_service_account_info_from_secrets():
    """
    Try to obtain a parsed service-account dict from st.secrets.
    Supports:
      - SERVICE_ACCOUNT_JSON (raw JSON string or dict)
      - SERVICE_ACCOUNT_JSON_BASE64 (base64-encoded JSON string, one or multi-line)
    """
    # Try JSON secret first
    sa_val = None
    try:
        sa_val = st.secrets.get("SERVICE_ACCOUNT_JSON", None)
    except Exception:
        sa_val = None

    if isinstance(sa_val, dict):
        return sa_val

    if isinstance(sa_val, str):
        s = sa_val.strip()
        # Clean triple quotes if user pasted with """ ... """
        if (s.startswith('"""') and s.endswith('"""')) or (s.startswith("'''") and s.endswith("'''")):
            s = s[3:-3].strip()
        try:
            return json.loads(s)
        except Exception:
            pass

    # Try base64 version
    sa_b64 = None
    try:
        sa_b64 = st.secrets.get("SERVICE_ACCOUNT_JSON_BASE64", None)
    except Exception:
        sa_b64 = None

    if sa_b64:
        if isinstance(sa_b64, str):
            # Remove whitespace/newlines
            compact_b64 = "".join(sa_b64.split())
            try:
                decoded = base64.b64decode(compact_b64).decode("utf-8")
                return json.loads(decoded)
            except Exception as e:
                st.error(f"Failed to decode SERVICE_ACCOUNT_JSON_BASE64: {e}")
                return None

    return None


def get_drive_service():
    """
    Build and return an authorized Google Drive v3 service using a Service Account.
    """
    sa_info = _get_service_account_info_from_secrets()
    if sa_info:
        creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    # fallback: path-based service account
    gpath = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gpath and os.path.exists(gpath):
        creds = service_account.Credentials.from_service_account_file(gpath, scopes=SCOPES)
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    raise RuntimeError("No usable service account found. Set SERVICE_ACCOUNT_JSON or SERVICE_ACCOUNT_JSON_BASE64 in Streamlit secrets, or GOOGLE_APPLICATION_CREDENTIALS env var.")
