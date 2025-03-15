from django.urls import path
from .views import google_drive_auth, google_drive_callback, upload_to_drive, list_drive_files, download_drive_file

urlpatterns = [
    path('auth/', google_drive_auth, name='google_drive_auth'),
    path('callback/', google_drive_callback, name='google_drive_callback'),
    path('upload/', upload_to_drive, name='upload_to_drive'),
    path('files/', list_drive_files, name='list_drive_files'),
    path('download/<str:file_id>/', download_drive_file, name='download_drive_file'),
]
