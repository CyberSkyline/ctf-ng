"""
Public file operations for sponsor-logos, event-cards, favicons
"""
import uuid
import logging
from flask import jsonify, request, current_app
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

# Allowed public folders and their content types
ALLOWED_FOLDERS = {
    'sponsor-logos': ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'],
    'event-cards': ['image/png', 'image/jpeg', 'image/webp'],
    'favicons': ['image/x-icon', 'image/png', 'image/svg+xml']
}

def generate_upload_url(args):
    """
    Generate presigned URL for client-side upload
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
        
        # Generate unique filename
        file_extension = get_file_extension(content_type)
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        object_key = f"{folder}/{filename}"
        
        # Generate presigned URL
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
    """Get presigned URL for public file access (no authentication required)"""
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
        
        # Verify file exists
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
    """List files in a public folder"""
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
            # Extract filename from key
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
        
        # If specific folder and filename provided
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
        
        # List files in specific folder or all folders
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
    """Get file extension from content type"""
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