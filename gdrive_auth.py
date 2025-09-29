# gdrive_auth.py  (robust replacement)
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
    Acceptable forms:
      - st.secrets["SERVICE_ACCOUNT_JSON"] contains a dict (if Streamlit parsed it)
      - contains the raw JSON string (with or without triple quotes)
      - contains a base64-encoded JSON string (if you stored base64)
      - st.secrets["SERVICE_ACCOUNT_JSON_BASE64"] contains base64 string
    Returns parsed dict or None.
    """
    # Try direct key first
    sa_val = None
    try:
        sa_val = st.secrets.get("SERVICE_ACCOUNT_JSON", None)
    except Exception:
        sa_val = None

    # Try base64 alt key next if needed
    sa_b64_alt = None
    try:
        sa_b64_alt = st.secrets.get("SERVICE_ACCOUNT_JSON_BASE64", None)
    except Exception:
        sa_b64_alt = None

    # 1) If it's already a dict (Streamlit may parse TOML into dict), return it
    if isinstance(sa_val, dict):
        return sa_val

    # 2) If we got a base64 secret in separate key, decode it
    if sa_b64_alt:
        try:
            decoded = base64.b64decode(sa_b64_alt).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            # fall through to other attempts
            pass

    # 3) If the secret is a string, try to normalize and parse it
    if isinstance(sa_val, str):
        s = sa_val.strip()
        # remove triple-quote wrappers if present (common when pasting JSON in TOML)
        if (s.startswith('"""') and s.endswith('"""')) or (s.startswith("'''") and s.endswith("'''")):
            s = s[3:-3].strip()

        # remove a single surrounding quote if the UI accidentally wrapped it
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            # remove outer single/double quotes
            s = s[1:-1]

        # Try raw JSON parse
        try:
            return json.loads(s)
        except Exception:
            pass

        # Try interpreting the string as base64 of JSON
        try:
            decoded = base64.b64decode(s).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            pass

        # Nothing worked
        # Provide minimal diagnostics (non-secret) to help debugging:
        # - length of string
        # - whether it contains typical JSON characters
        info = {
            "length": len(s),
            "has_open_brace": "{" in s,
            "has_private_key_marker": "PRIVATE KEY" in s or "BEGIN PRIVATE KEY" in s
        }
        # Do NOT display the secret itself
        st.error("SERVICE_ACCOUNT_JSON found but could not be parsed as JSON or base64. See diagnostics below.")
        st.write("Diagnostic info (non-sensitive):", info)
        return None

    # 4) nothing found
    return None


def get_drive_service():
    """
    Build and return an authorized Google Drive v3 service using a Service Account.
    It reads st.secrets['SERVICE_ACCOUNT_JSON'] or the fallback env var GOOGLE_APPLICATION_CREDENTIALS.
    Raises RuntimeError with guidance if it can't build credentials.
    """
    # try secrets-based SA
    sa_info = None
    try:
        sa_info = _get_service_account_info_from_secrets()
    except Exception as e:
        sa_info = None

    if sa_info:
        try:
            creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
            return build("drive", "v3", credentials=creds, cache_discovery=False)
        except Exception as e:
            raise RuntimeError(f"Failed to create credentials from SERVICE_ACCOUNT_JSON: {e}")

    # fallback: path-based service account (local or env)
    gpath = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gpath and os.path.exists(gpath):
        try:
            creds = service_account.Credentials.from_service_account_file(gpath, scopes=SCOPES)
            return build("drive", "v3", credentials=creds, cache_discovery=False)
        except Exception as e:
            raise RuntimeError(f"Failed to create credentials from GOOGLE_APPLICATION_CREDENTIALS file: {e}")

    raise RuntimeError(
        "No usable service account found. Set SERVICE_ACCOUNT_JSON in Streamlit secrets (raw JSON or base64) "
        "or set environment variable GOOGLE_APPLICATION_CREDENTIALS with path to JSON key."
    )
