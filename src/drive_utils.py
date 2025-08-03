"""Google Drive utilities for fetching random images."""

from __future__ import annotations

import os
import random
import json
from typing import NamedTuple
from io import BytesIO

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import DRIVE_FOLDERS, MAX_RETRIES


class DriveFile(NamedTuple):
    """Represents a file from Google Drive."""
    id: str
    name: str
    web_view_link: str


class DriveService:
    """Google Drive API service wrapper."""
    
    def __init__(self, service_account_path: str) -> None:
        """Initialize the Google Drive service.
        
        Args:
            service_account_path: Path to service account JSON file.
        """
        self.service_account_path = service_account_path
        self.service = None
        self._file_cache: dict[str, list[DriveFile]] = {}
        
    def _init_service(self) -> None:
        """Initialize the Google Drive service with authentication."""
        if self.service is not None:
            return
            
        print(f"🔐 Initializing Google Drive service...")
        print(f"🔐 Service account path: {self.service_account_path}")
        print(f"🔐 File exists: {os.path.exists(self.service_account_path)}")
        
        if os.path.exists(self.service_account_path):
            file_size = os.path.getsize(self.service_account_path)
            print(f"🔐 Service account file size: {file_size} bytes")
            
            # Check if it's valid JSON
            try:
                with open(self.service_account_path, 'r') as f:
                    service_account_data = json.load(f)
                print(f"🔐 Service account JSON keys: {list(service_account_data.keys())}")
                if 'type' in service_account_data:
                    print(f"🔐 Service account type: {service_account_data['type']}")
            except Exception as json_error:
                print(f"❌ Error reading service account JSON: {json_error}")
        
        try:
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            print(f"✅ Service account credentials loaded successfully")
            
            # Build the service
            self.service = build('drive', 'v3', credentials=credentials)
            print(f"✅ Google Drive service built successfully")
            
        except Exception as auth_error:
            print(f"❌ Error initializing Google Drive service: {auth_error}")
            print(f"❌ Error type: {type(auth_error).__name__}")
            raise

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    def _get_folder_files(self, folder_name: str) -> list[DriveFile]:
        """Get all image files from a specific folder.
        
        Args:
            folder_name: Name of the folder to search.
            
        Returns:
            List of DriveFile objects.
        """
        self._init_service()
        
        print(f"📁 Looking for folder: {folder_name}")
        
        # First, find the folder by name
        folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        print(f"📁 Folder query: {folder_query}")
        
        try:
            folder_results = self.service.files().list(
                q=folder_query,
                fields="files(id, name)"
            ).execute()
            print(f"✅ Folder search completed")
        except Exception as folder_error:
            print(f"❌ Error searching for folder: {folder_error}")
            print(f"❌ Error type: {type(folder_error).__name__}")
            raise
        
        folders = folder_results.get('files', [])
        print(f"📁 Found {len(folders)} matching folders")
        
        if not folders:
            raise ValueError(f"Folder '{folder_name}' not found in Google Drive")
        
        folder_id = folders[0]['id']
        print(f"📁 Using folder ID: {folder_id}")
        
        # Get all image files from the folder (filter for supported formats)
        image_query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/gif' or mimeType='image/bmp' or mimeType='image/tiff')"
        print(f"🖼️  Image query: {image_query}")
        
        try:
            results = self.service.files().list(
                q=image_query,
                fields="files(id, name, webViewLink)",
                pageSize=1000
            ).execute()
            print(f"✅ Image search completed")
        except Exception as image_error:
            print(f"❌ Error searching for images: {image_error}")
            print(f"❌ Error type: {type(image_error).__name__}")
            raise
        
        files = results.get('files', [])
        
        # Additional filtering by file extension for safety
        supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
        filtered_files = [
            DriveFile(
                id=file['id'],
                name=file['name'],
                web_view_link=file['webViewLink']
            )
            for file in files
            if file['name'].lower().endswith(supported_extensions)
        ]
        
        return filtered_files

    def _get_cached_files(self, folder_name: str) -> list[DriveFile]:
        """Get files from cache or fetch from Drive if not cached.
        
        Args:
            folder_name: Name of the folder.
            
        Returns:
            List of DriveFile objects.
        """
        if folder_name not in self._file_cache:
            self._file_cache[folder_name] = self._get_folder_files(folder_name)
        return self._file_cache[folder_name]

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    def _download_file(self, file_id: str) -> bytes:
        """Download a file's content as bytes.
        
        Args:
            file_id: Google Drive file ID.
            
        Returns:
            File content as bytes.
        """
        self._init_service()
        
        request = self.service.files().get_media(fileId=file_id)
        file_buffer = BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_bytes = file_buffer.getvalue()
        
        # Debug: Check the downloaded file format
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(file_bytes))
            print(f"📥 Downloaded image: {len(file_bytes)} bytes, format={img.format}, mode={img.mode}, size={img.size}")
        except Exception as img_error:
            print(f"⚠️  Downloaded file may not be a valid image: {img_error}")
        
        return file_bytes

    def get_random_file_bytes(self, folder_name: str) -> tuple[bytes, str]:
        """Get random file bytes and URL from a specific folder.
        
        Args:
            folder_name: Name of the Google Drive folder.
            
        Returns:
            Tuple of (file_bytes, public_url).
            
        Raises:
            ValueError: If folder is empty or not found.
        """
        files = self._get_cached_files(folder_name)
        
        if not files:
            raise ValueError(f"No files found in folder '{folder_name}'")
        
        # Select random file
        random_file = random.choice(files)
        
        # Download file content
        file_bytes = self._download_file(random_file.id)
        
        return file_bytes, random_file.web_view_link

    def refresh_cache(self) -> None:
        """Refresh the file cache for all folders."""
        self._file_cache.clear()
        
        # Pre-populate cache for all configured folders
        for folder_name in DRIVE_FOLDERS.values():
            try:
                self._get_cached_files(folder_name)
            except Exception as e:
                print(f"Warning: Could not cache folder '{folder_name}': {e}")


# Global service instance
_drive_service: DriveService | None = None


def init_service() -> DriveService:
    """Initialize and return the global Drive service instance.
    
    Returns:
        DriveService instance.
    """
    global _drive_service
    
    if _drive_service is None:
        service_account_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not service_account_path:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
        
        _drive_service = DriveService(service_account_path)
        
    return _drive_service


def get_random_file_bytes(folder_key: str) -> tuple[bytes, str]:
    """Get random file bytes and URL from a configured folder.
    
    Args:
        folder_key: Key from DRIVE_FOLDERS config (e.g., 'HOOK', 'SCREEN', 'CTA').
        
    Returns:
        Tuple of (file_bytes, public_url).
    """
    if folder_key not in DRIVE_FOLDERS:
        raise ValueError(f"Unknown folder key: {folder_key}")
    
    folder_name = DRIVE_FOLDERS[folder_key]
    service = init_service()
    
    return service.get_random_file_bytes(folder_name) 