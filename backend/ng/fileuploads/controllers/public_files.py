"""
Public file operations for sponsor-logos, event-cards, favicons
"""
import uuid
import logging
import requests
from flask import request
from werkzeug.datastructures import FileStorage

from ... import config

logger = logging.getLogger(__name__)

ALLOWED_FOLDERS = config.PUBLIC_FILE_ALLOWED_FOLDERS

def generate_upload_url(args):
    """
    Generate presigned URL for client-side upload to public S3 folders

    This function creates a presigned URL that allows clients to upload files
    directly to S3 without routing through the server, improving performance
    and reducing server load.

    Args:
        args (dict): Request arguments containing:
            - folder (str): Target folder (sponsor-logos, event-cards, favicons)
            - content_type (str): MIME type of file to upload

    Returns:
        tuple: (response_dict, status_code) where response_dict contains:
            - presigned_url: S3 presigned URL for PUT request
            - filename: Generated UUID-based filename
            - object_key: Full S3 object key (folder/filename)
            - content_type: Validated content type
            - upload_method: HTTP method (PUT)

    Raises:
        400: Invalid folder or content type
        500: Internal server error
        503: S3 storage not configured
    """
    try:
        folder = args.get('folder')
        content_type = args.get('content_type')

        if not folder or folder not in ALLOWED_FOLDERS:
            return {
                "error": f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}"
            }, 400

        if not content_type or content_type not in ALLOWED_FOLDERS[folder]:
            return {
                "error": f"Invalid content type for {folder}. Allowed: {', '.join(ALLOWED_FOLDERS[folder])}"
            }, 400

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return {"error": "File storage not configured"}, 503

        file_extension = get_file_extension(content_type)
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        object_key = f"{folder}/{filename}"

        result = s3_service.generate_upload_url(folder, filename, content_type)

        return {
            "presigned_url": result['presigned_url'],
            "filename": filename,
            "object_key": object_key,
            "content_type": content_type,
            "upload_method": "PUT"
        }

    except Exception as e:
        logger.error(f"Upload URL generation error: {e}")
        return {"error": "Internal server error"}, 500

def get_public_file(args):
    """
    Get presigned download URL for public file access (no authentication required)

    Generates a secure, time-limited download URL for public files stored in S3.
    URLs are valid for 24 hours and allow direct access to the file content.

    Args:
        args (dict): Request arguments containing:
            - folder (str): Folder containing the file
            - filename (str): Name of the file to access

    Returns:
        tuple: (response_dict, status_code) where response_dict contains:
            - url: Presigned download URL (expires in 24 hours)
            - filename: Original filename
            - folder: Folder name
            - object_key: Full S3 object key

    Raises:
        400: Missing folder or filename parameter
        404: File not found or invalid folder
        500: Internal server error
        503: S3 storage not configured
    """
    try:
        folder = args.get('folder')
        filename = args.get('filename')

        if not folder or not filename:
            return {"error": "Folder and filename are required"}, 400

        if folder not in ALLOWED_FOLDERS:
            return {"error": "Invalid folder"}, 404

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return {"error": "File storage not configured"}, 503

        object_key = f"{folder}/{filename}"

        if not s3_service.object_exists(object_key):
            return {"error": "File not found"}, 404

        presigned_url = s3_service.generate_download_url(object_key, expires_in=86400)

        logger.info(f"Generated download URL for {object_key}")

        return {
            "url": presigned_url,
            "filename": filename,
            "folder": folder,
            "object_key": object_key
        }

    except Exception as e:
        logger.error(f"Get public file error: {e}")
        return {"error": "File not found"}, 404

def list_public_files(args):
    """
    List all files in a specified public folder

    Retrieves metadata for all files in the specified folder from S3 storage.
    Returns comprehensive file information including size and modification dates.

    Args:
        args (dict): Request arguments containing:
            - folder (str): Folder to list files from

    Returns:
        tuple: (response_dict, status_code) where response_dict contains:
            - folder: Folder name
            - files: List of file objects with metadata
            - count: Total number of files

    Each file object contains:
        - filename: File name
        - size: File size in bytes
        - last_modified: ISO timestamp of last modification
        - key: Full S3 object key

    Raises:
        400: Invalid or missing folder parameter
        500: Internal server error
        503: S3 storage not configured
    """
    try:
        folder = args.get('folder')

        if not folder or folder not in ALLOWED_FOLDERS:
            return {"error": "Valid folder parameter required"}, 400

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return {"error": "File storage not configured"}, 503

        objects = s3_service.list_objects(prefix=folder)
        files = []

        for obj in objects:
            key_parts = obj['key'].split('/')
            if len(key_parts) > 1 and key_parts[0] == folder:
                files.append({
                    'filename': key_parts[1],
                    'size': obj['size'],
                    'last_modified': obj['last_modified'],
                    'key': obj['key']
                })

        return {
            "folder": folder,
            "files": files,
            "count": len(files)
        }

    except Exception as e:
        logger.error(f"List public files error: {e}")
        return {"error": "Internal server error"}, 500

def search_public_files():
    """
    Search files across folders or within specific folder with flexible parameters

    Provides comprehensive file search functionality supporting multiple modes:
    - List all files in a folder (folder parameter only)
    - Search by filename pattern across all folders (filename parameter only)
    - Search by filename pattern within specific folder (both parameters)

    Query parameters are read directly from Flask request.args:
        - folder (str, optional): Specific folder to search in
        - filename (str, optional): Filename pattern to search for
        - limit (int, optional): Max results (default 10, max 50)

    Returns:
        tuple: (response_dict, status_code) where response_dict contains:
            - success: Boolean indicating operation success
            - data: Search results object with:
                - files: List of matching file objects
                - total_count: Number of results returned
                - folder: Target folder (or 'all' for cross-folder)
                - query: Search pattern (if provided)
                - search_type: Type of search performed

    Each file object contains:
        - filename: File name
        - folder: Folder containing the file
        - size: File size in bytes
        - last_modified: ISO timestamp
        - key: Full S3 object key

    Raises:
        400: Invalid search parameters
        500: Internal server error
        503: S3 storage not configured
    """
    try:
        folder = request.args.get('folder')
        filename = request.args.get('filename')

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return {"error": "File storage not configured"}, 503

        if folder and folder not in ALLOWED_FOLDERS:
            return {"error": "Invalid folder"}, 400

        if folder and filename:
            object_key = f"{folder}/{filename}"
            if s3_service.object_exists(object_key):
                return {
                    "files": [{
                        'filename': filename,
                        'folder': folder,
                        'key': object_key
                    }],
                    "count": 1
                }
            else:
                return {
                    "files": [],
                    "count": 0
                }

        if folder:
            prefix = folder
        else:
            prefix = ""

        objects = s3_service.list_objects(prefix=prefix)
        files = []

        for obj in objects:
            key_parts = obj['key'].split('/')
            if len(key_parts) > 1 and key_parts[0] in ALLOWED_FOLDERS:
                files.append({
                    'filename': key_parts[1],
                    'folder': key_parts[0],
                    'size': obj['size'],
                    'last_modified': obj['last_modified'],
                    'key': obj['key']
                })

        return {
            "folder": folder,
            "files": files,
            "count": len(files)
        }

    except Exception as e:
        logger.error(f"Search public files error: {e}")
        return {"error": "Internal server error"}, 500

def get_file_extension(content_type: str) -> str:
    """
    Get appropriate file extension from MIME content type

    Maps MIME types to standard file extensions for consistent file naming.
    Used internally by upload functions to ensure proper file extensions.

    Args:
        content_type (str): MIME type (e.g., 'image/png', 'image/jpeg')

    Returns:
        str: File extension without dot (e.g., 'png', 'jpg', 'webp')
             Returns 'bin' for unknown content types

    Supported content types:
        - image/png -> png
        - image/jpeg -> jpg
        - image/jpg -> jpg
        - image/webp -> webp
        - image/svg+xml -> svg
        - image/x-icon -> ico
        - application/octet-stream -> bin
    """
    extension_map = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'image/webp': 'webp',
        'image/svg+xml': 'svg',
        'image/x-icon': 'ico',
        'application/octet-stream': 'bin'
    }
    return extension_map.get(content_type, 'bin')

def direct_upload_file(args):
    """
    Upload a file directly to S3 using server-side presigned URL generation

    This function provides a complete server-side upload workflow:
    1. Validates the uploaded file and target folder
    2. Generates a presigned upload URL
    3. Uploads the file directly to S3
    4. Returns comprehensive file metadata

    This is an alternative to client-side uploads for cases where the client
    cannot or should not handle the S3 upload directly.

    Args:
        args (dict): Request arguments containing:
            - folder (str): Target folder for upload
            - file (FileStorage): Uploaded file object

    Returns:
        tuple: (response_dict, status_code) where response_dict contains:
            - success: Boolean indicating upload success
            - file_info: Object with file metadata including:
                - object_key: Full S3 object key
                - filename: Generated UUID filename
                - original_filename: Original uploaded filename
                - folder: Target folder
                - content_type: Validated MIME type
                - file_size: File size in bytes

    Raises:
        400: Invalid folder, missing file, or unsupported content type
        500: Upload failed or internal server error
        503: S3 storage not configured
    """
    try:
        folder = args.get('folder')
        file = args.get('file')

        if not folder or folder not in ALLOWED_FOLDERS:
            return {
                "error": f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}"
            }, 400

        if not file or not isinstance(file, FileStorage) or not file.filename:
            return {"error": "Valid file is required"}, 400

        # Get content type
        content_type = file.content_type or 'application/octet-stream'
        if content_type not in ALLOWED_FOLDERS[folder]:
            return {
                "error": f"Invalid content type for {folder}. Allowed: {', '.join(ALLOWED_FOLDERS[folder])}"
            }, 400

        # Generate presigned URL
        presigned_response = generate_upload_url({
            'folder': folder,
            'content_type': content_type
        })

        if isinstance(presigned_response, tuple):
            return presigned_response

        presigned_url = presigned_response.get('presigned_url')
        object_key = presigned_response.get('object_key')

        if not presigned_url:
            return {"error": "Failed to generate presigned URL"}, 500

        file.stream.seek(0, 2)
        file_size = file.stream.tell()
        file.stream.seek(0)
        file_data = file.stream.read()
        file.stream.seek(0)

        upload_response = requests.put(
            presigned_url,
            data=file_data,
            headers={'Content-Type': content_type},
            timeout=60
        )

        if upload_response.status_code not in [200, 204]:
            logger.error(f"S3 upload failed: HTTP {upload_response.status_code}")
            return {"error": "Failed to upload file to S3"}, 500

        logger.info(f"Successfully uploaded file to S3: {object_key}")

        return {
            "success": True,
            "file_info": {
                "object_key": object_key,
                "filename": presigned_response.get('filename'),
                "original_filename": file.filename,
                "folder": folder,
                "content_type": content_type,
                "file_size": file_size
            }
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"error": "Upload failed"}, 500