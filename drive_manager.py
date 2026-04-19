"""
Google Drive Manager for ltxflow pipeline.
Usage:
  python drive_manager.py download_state
  python drive_manager.py upload_state
"""

import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]

DRIVE_TOKEN_FILE = Path("drive_token.json")
FOLDER_ID        = os.environ.get("GDRIVE_FOLDER_ID", "")
STATE_FILES      = ["tracker.json", "checkpoint.json", "yt_token.json"]

def get_service():
    creds = None
    if DRIVE_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(DRIVE_TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(DRIVE_TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError("No valid Drive token. Run drive_manager.py auth on your PC.")
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def find_file(service, name, parent_id):
    q = f"name='{name}' and '{parent_id}' in parents and trashed=false"
    res = service.files().list(q=q, fields="files(id,name)").execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def download_file(service, file_id, dest_path):
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request, chunksize=4*1024*1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    print(f"  Downloaded: {dest_path.name}")

def upload_file(service, local_path, parent_id, mime="application/json"):
    local_path = Path(local_path)
    existing_id = find_file(service, local_path.name, parent_id)
    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
    if existing_id:
        service.files().update(fileId=existing_id, media_body=media).execute()
    else:
        meta = {"name": local_path.name, "parents": [parent_id]}
        service.files().create(body=meta, media_body=media, fields="id").execute()
    print(f"  Uploaded: {local_path.name}")

def download_state():
    print("Downloading state from Drive...")
    service = get_service()
    for fname in STATE_FILES:
        fid = find_file(service, fname, FOLDER_ID)
        if fid:
            download_file(service, fid, fname)
        else:
            print(f"  Not in Drive: {fname}")
    print("Done.")

def upload_state():
    print("Uploading state to Drive...")
    service = get_service()
    for fname in STATE_FILES:
        if Path(fname).exists():
            upload_file(service, fname, FOLDER_ID)
    if DRIVE_TOKEN_FILE.exists():
        upload_file(service, DRIVE_TOKEN_FILE, FOLDER_ID)
    print("Done.")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "download_state": download_state()
    elif cmd == "upload_state": upload_state()
    else: print("Commands: download_state | upload_state")
