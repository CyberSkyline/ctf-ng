"""
Public file operations for sponsor-logos, event-cards, favicons
"""
import uuid
import logging
import requests
from ...core.utils import success_response, error_response
from flask import request
from werkzeug.datastructures import FileStorage

from ... import config

logger = logging.getLogger(__name__)

ALLOWED_FOLDERS = config.PUBLIC_FILE_ALLOWED_FOLDERS

def generate_upload_url(args):
    """Generate presigned URL for direct client-side upload to S3"""
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
    """Get presigned download URL for public file access"""
    try:
        folder = args.get('folder')
        filename = args.get('filename')

        if not folder or not filename:
            return error_response("Folder and filename are required", 400)

        if folder not in ALLOWED_FOLDERS:
            return error_response("Invalid folder", 404)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", 503)

        object_key = f"{folder}/{filename}"

        if not s3_service.object_exists(object_key):
            return error_response("File not found", 404)

        presigned_url = s3_service.generate_download_url(object_key, expires_in=86400)

        logger.info(f"Generated download URL for {object_key}")

        return success_response({
            "url": presigned_url,
            "filename": filename,
            "folder": folder,
            "object_key": object_key
        })

    except Exception as e:
        logger.error(f"Get public file error: {e}")
        return error_response("File not found", 404)

def list_public_files(args):
    """List all files in a specified public folder"""
    try:
        folder = args.get('folder')

        if not folder or folder not in ALLOWED_FOLDERS:
            return error_response("Valid folder parameter required", 400)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", 503)

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

        return success_response({
            "folder": folder,
            "files": files,
            "count": len(files)
        })

    except Exception as e:
        logger.error(f"List public files error: {e}")
        return {"error": "Internal server error"}, 500

def search_public_files():
    """Search files across folders or within specific folder"""
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
    """Get file extension from MIME content type"""
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
    """Upload file directly to S3 using server-side presigned URL generation"""
    try:
        folder = args.get('folder')
        file = args.get('file')

        if not folder or folder not in ALLOWED_FOLDERS:
            return error_response(f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}", 400)

        if not file or not isinstance(file, FileStorage) or not file.filename:
            return error_response("Valid file is required", 400)

        content_type = file.content_type or 'application/octet-stream'
        if content_type not in ALLOWED_FOLDERS[folder]:
            return error_response(f"Invalid content type for {folder}. Allowed: {', '.join(ALLOWED_FOLDERS[folder])}", 400)

        presigned_response = generate_upload_url({
            'folder': folder,
            'content_type': content_type
        })

        if isinstance(presigned_response, tuple):
            return presigned_response

        presigned_url = presigned_response.get('presigned_url')
        object_key = presigned_response.get('object_key')

        if not presigned_url:
            return error_response("Failed to generate presigned URL", 500)

        file.stream.seek(0)
        file_data = file.stream.read()
        file_size = len(file_data)

        upload_response = requests.put(
            presigned_url,
            data=file_data,
            headers={'Content-Type': content_type},
            timeout=60
        )

        if upload_response.status_code not in [200, 204]:
            logger.error(f"S3 upload failed: HTTP {upload_response.status_code}")
            return error_response("Failed to upload file to S3", 500)

        logger.info(f"Successfully uploaded file to S3: {object_key}")

        return success_response({
            "object_key": object_key,
            "filename": presigned_response.get('filename'),
            "original_filename": file.filename,
            "folder": folder,
            "content_type": content_type,
            "file_size": file_size
        })

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"error": "Upload failed"}, 500