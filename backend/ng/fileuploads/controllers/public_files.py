"""
Public file operations for sponsor-logos, event-cards, favicons
"""
import logging
import requests
from ...core.utils import success_response, error_response
from werkzeug.datastructures import FileStorage

from ... import config

logger = logging.getLogger(__name__)

ALLOWED_FOLDERS = config.PUBLIC_FILE_ALLOWED_FOLDERS
MAX_AUTO_NUMBER_ATTEMPTS = config.PUBLIC_FILE_AUTO_NUMBER_MAX_ATTEMPTS

def generate_unique_filename(s3_service, folder, original_filename, allow_overwrite=False):
    """Generate unique filename by appending numbers if file exists"""
    if allow_overwrite:
        return original_filename

    object_key = f"{folder}/{original_filename}"
    exists = s3_service.object_exists(object_key)

    if not exists:
        return original_filename

    if '.' in original_filename:
        name, ext = original_filename.rsplit('.', 1)
        ext = '.' + ext
    else:
        name = original_filename
        ext = ''

    counter = 1
    while counter <= MAX_AUTO_NUMBER_ATTEMPTS:
        numbered_filename = f"{name}_{counter}{ext}"
        numbered_key = f"{folder}/{numbered_filename}"
        if not s3_service.object_exists(numbered_key):
            return numbered_filename
        counter += 1

    raise ValueError(f"Could not generate unique filename for '{original_filename}' after {MAX_AUTO_NUMBER_ATTEMPTS} attempts. Too many files with similar names exist.")

def generate_upload_url(args):
    """Generate presigned URL for direct client-side upload to S3"""
    try:
        folder = args.get('folder')
        content_type = args.get('content_type')
        filename = args.get('filename')
        allow_overwrite = args.get('allow_overwrite', False)

        if not folder or folder not in ALLOWED_FOLDERS:
            return error_response(
                f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}",
                "folder", 400
            )

        if not content_type or content_type not in ALLOWED_FOLDERS[folder]:
            return error_response(
                f"Invalid content type for {folder}. Allowed: {', '.join(ALLOWED_FOLDERS[folder])}",
                "content_type", 400
            )

        if not filename:
            return error_response("Filename is required", "filename", 400)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", "s3_service", 503)

        # Generate unique filename or allow overwrite
        try:
            final_filename = generate_unique_filename(s3_service, folder, filename, allow_overwrite)
        except ValueError as e:
            logger.warning(f"Filename generation failed for '{filename}' in folder '{folder}': {e}")
            return error_response(str(e), "filename_generation", 409)

        result = s3_service.generate_upload_url(folder, final_filename, content_type)

        uploaded_file = {
            "filename": final_filename,
            "folder": folder,
        }

        uploaded_file["upload_url"] = result['presigned_url']
        uploaded_file["upload_method"] = "PUT"

        # Optionally include download URL
        include_urls = args.get('include_urls', False)
        if include_urls:
            object_key = f"{folder}/{final_filename}"
            download_url = s3_service.generate_download_url(object_key, expires_in=config.S3_DOWNLOAD_URL_EXPIRATION)
            uploaded_file["download_url"] = download_url

        return success_response(uploaded_file)

    except Exception as e:
        logger.error(f"Upload URL generation error: {e}")
        return error_response("Internal server error", "upload", 500)

def get_public_file(args):
    """Get presigned download URL for public file access"""
    try:
        folder = args.get('folder')
        filename = args.get('filename')

        if not folder or not filename:
            return error_response("Folder and filename are required", "parameters", 400)

        if folder not in ALLOWED_FOLDERS:
            return error_response("Invalid folder", "folder", 404)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", "s3_service", 503)

        object_key = f"{folder}/{filename}"
        if not s3_service.object_exists(object_key):
            return error_response("File not found", "file", 404)

        presigned_url = s3_service.generate_download_url(object_key, expires_in=config.S3_DOWNLOAD_URL_EXPIRATION)

        logger.info(f"Generated download URL for {object_key}")

        return success_response({
            "download_url": presigned_url,
            "filename": filename,
            "folder": folder,
        })

    except Exception as e:
        logger.error(f"Get public file error: {e}")
        return error_response("File not found", "file", 404)

def list_public_files(args):
    """List all files in a specified public folder"""
    try:
        folder = args.get('folder')
        include_urls = args.get('include_urls', False)

        if not folder or folder not in ALLOWED_FOLDERS:
            return error_response("Valid folder parameter required", "folder", 400)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", "s3_service", 503)

        objects = s3_service.list_objects(prefix=folder)
        files = []

        for obj in objects:
            key_parts = obj['key'].split('/')
            if len(key_parts) > 1 and key_parts[0] == folder:
                file_info = {
                    'filename': key_parts[1],
                    'folder': folder,
                    'last_modified': obj['last_modified']
                }

                # Add presigned download URL if requested
                if include_urls:
                    try:
                        presigned_url = s3_service.generate_download_url(obj['key'], expires_in=config.S3_DOWNLOAD_URL_EXPIRATION)
                        file_info['download_url'] = presigned_url
                    except Exception as e:
                        logger.warning(f"Failed to generate download URL for {obj['key']}: {e}")
                        file_info['download_url'] = None
                files.append(file_info)

        return success_response({
            "files": files,
        })

    except Exception as e:
        logger.error(f"List public files error: {e}")
        return error_response("Internal server error", "list", 500)

def search_public_files(args):
    """Search files across folders or within specific folder"""
    try:
        folder = args.get('folder')
        filename = args.get('filename')
        include_urls = args.get('include_urls', False)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", "s3_service", 503)

        if folder and folder not in ALLOWED_FOLDERS:
            return error_response("Invalid folder", "folder", 400)

        if folder and filename:
            object_key = f"{folder}/{filename}"
            if s3_service.object_exists(object_key):
                file_info = {
                    'filename': filename,
                    'folder': folder
                }

                # Add download URL if requested
                if include_urls:
                    try:
                        download_url = s3_service.generate_download_url(object_key, expires_in=config.S3_DOWNLOAD_URL_EXPIRATION)
                        file_info['download_url'] = download_url
                    except Exception as e:
                        logger.warning(f"Failed to generate download URL for {object_key}: {e}")
                        file_info['download_url'] = None

                return success_response({
                    "files": [file_info],
                })
            else:
                return success_response({
                    "files": [],
                })

        if folder:
            prefix = folder
        else:
            prefix = ""

        objects = s3_service.list_objects(prefix=prefix)
        files = []

        for obj in objects:
            key_parts = obj['key'].split('/')
            if len(key_parts) > 1 and key_parts[0] in ALLOWED_FOLDERS:
                file_info = {
                    'filename': key_parts[1],
                    'folder': key_parts[0],
                    'last_modified': obj['last_modified']
                }

                # Add download URL if requested
                if include_urls:
                    try:
                        download_url = s3_service.generate_download_url(obj['key'], expires_in=config.S3_DOWNLOAD_URL_EXPIRATION)
                        file_info['download_url'] = download_url
                    except Exception as e:
                        logger.warning(f"Failed to generate download URL for {obj['key']}: {e}")
                        file_info['download_url'] = None

                files.append(file_info)

        return success_response({
            "folder": folder,
            "files": files,
            "count": len(files)
        })

    except Exception as e:
        logger.error(f"Search public files error: {e}")
        return error_response("Internal server error", "search", 500)

def direct_upload_file(args):
    """Upload file directly to S3 using server-side presigned URL generation"""
    try:
        folder = args.get('folder')
        file = args.get('file')

        if not folder or folder not in ALLOWED_FOLDERS:
            return error_response(f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}", "folder", 400)

        if not file or not isinstance(file, FileStorage) or not file.filename:
            return error_response("Valid file is required", "file", 400)

        content_type = file.content_type or 'application/octet-stream'
        if content_type not in ALLOWED_FOLDERS[folder]:
            return error_response(
                f"Invalid content type for {folder}. Allowed: {', '.join(ALLOWED_FOLDERS[folder])}",
                "content_type", 400
            )

        original_filename = file.filename
        allow_overwrite = args.get('allow_overwrite', False)

        from ...core.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return error_response("File storage not configured", "s3_service", 503)

        # Generate unique filename or allow overwrite
        try:
            final_filename = generate_unique_filename(s3_service, folder, original_filename, allow_overwrite)
        except ValueError as e:
            logger.warning(f"Filename generation failed for '{original_filename}' in folder '{folder}': {e}")
            return error_response(str(e), "filename_generation", 409)

        # Generate presigned URL for the actual upload
        result = s3_service.generate_upload_url(folder, final_filename, content_type)
        presigned_url = result['presigned_url']
        object_key = f"{folder}/{final_filename}"

        if not presigned_url:
            return error_response("Failed to generate presigned URL", "presigned_url", 500)

        file.stream.seek(0)
        file_data = file.stream.read()

        upload_response = requests.put(
            presigned_url,
            data=file_data,
            headers={'Content-Type': content_type},
            timeout=60
        )

        if upload_response.status_code not in [200, 204]:
            logger.error(f"S3 upload failed: HTTP {upload_response.status_code}")
            return error_response("Failed to upload file to S3", "s3_upload", 500)

        logger.info(f"Successfully uploaded file to S3: {object_key}")

        uploaded_file = {
            "filename": final_filename,
            "folder": folder,
        }

        # Optionally include download URL
        include_urls = args.get('include_urls', False)  # Default to False for upload endpoints
        if include_urls:
            try:
                download_url = s3_service.generate_download_url(object_key, expires_in=config.S3_DOWNLOAD_URL_EXPIRATION)
                uploaded_file["download_url"] = download_url
                logger.info(f"Generated download URL for newly uploaded file: {object_key}")
            except Exception as e:
                logger.error(f"Failed to generate download URL for {final_filename}: {e}")
                uploaded_file["download_url"] = None

        return success_response(uploaded_file)

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return error_response("Upload failed", "upload", 500)