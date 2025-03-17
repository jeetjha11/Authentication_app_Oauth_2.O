import tempfile

from django.shortcuts import render

# Create your views here.

from django.views.decorators.csrf import csrf_exempt
import os
import pickle
from django.http import JsonResponse, FileResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'drive/credentials.json'
TOKEN_FILE = 'drive/token.pickle'


# Google Drive Authentication

def google_drive_auth(request):
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=8000, open_browser=True)

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return JsonResponse({"message": "Google Drive authentication successful!"})


def google_drive_callback(request):
    return JsonResponse({"message": "Google Drive callback triggered!"})


@csrf_exempt
def upload_to_drive(request):
    if request.method == "POST" and request.FILES.get("file"):
        creds = None

        # ✅ Load Google Drive credentials
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            return JsonResponse({"error": "Google Drive authentication required"}, status=401)

        service = build("drive", "v3", credentials=creds)
        uploaded_file = request.FILES["file"]

        try:
            # ✅ Read file content into memory
            file_stream = io.BytesIO(uploaded_file.read())

            # ✅ Upload directly from memory
            file_metadata = {"name": uploaded_file.name}
            media = MediaIoBaseUpload(file_stream, mimetype=uploaded_file.content_type, resumable=True)
            drive_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            return JsonResponse({"message": "File uploaded successfully!", "file_id": drive_file.get("id")})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "No file provided"}, status=400)


@csrf_exempt
def list_drive_files(request):
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        return JsonResponse({"error": "Google Drive authentication required"}, status=401)

    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(fields="files(id, name)").execute()
    files = results.get('files', [])

    return JsonResponse({"files": files})


def download_drive_file(request, file_id):
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        return JsonResponse({"error": "Google Drive authentication required"}, status=401)

    service = build('drive', 'v3', credentials=creds)
    request_file = service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request_file)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_io.seek(0)
    return FileResponse(file_io, as_attachment=True, filename=f"{file_id}.pdf")
