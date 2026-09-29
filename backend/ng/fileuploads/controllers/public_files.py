"""
Public file operations for sponsor-logos, event-cards, favicons
"""
import requests
from ...core.exceptions import APIException
from ...core.utils import success_response, error_response
from ...core.utils.logger import get_logger
from werkzeug.datastructures import FileStorage

from ... import config

logger = get_logger(__name__)

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
    """
    Generate presigned URL for direct client-side upload to S3.

    No catch-all here for anything past this point: the route this is called
    from is already wrapped in `@handle_exceptions`, which reports and traces
    an unanticipated failure on its own - a local `except Exception` would
    only duplicate that, with a less specific message.
    """
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
        logger.warning("Filename generation failed for '%s' in folder '%s': %s", filename, folder, e)
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

def get_public_file(args):
    """Get presigned download URL for public file access. No catch-all: see `generate_upload_url`."""
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

    logger.info("Generated download URL for %s", object_key)

    return success_response({
        "download_url": presigned_url,
        "filename": filename,
        "folder": folder,
    })

def list_public_files(args):
    """List all files in a specified public folder. No catch-all: see `generate_upload_url`."""
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
                    logger.warning("Failed to generate download URL for %s: %s", obj['key'], e)
                    file_info['download_url'] = None
            files.append(file_info)

    return success_response({
        "files": files,
    })

def search_public_files(args):
    """Search files across folders or within specific folder. No catch-all: see `generate_upload_url`."""
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
                    logger.warning("Failed to generate download URL for %s: %s", object_key, e)
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
                    logger.warning("Failed to generate download URL for %s: %s", obj['key'], e)
                    file_info['download_url'] = None

            files.append(file_info)

    return success_response({
        "files": files,
    })

def direct_upload_file(args):
    """
    Upload file directly to S3 using server-side presigned URL generation.

    No catch-all: see `generate_upload_url`. The two failures below raise
    `APIException` (defaults to 500) rather than building an error response
    directly, for the same reason - the central handler reports and traces
    them on its own once they propagate, and there is no exception here to
    wrap in `report_unexpected` in the first place.
    """
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
        logger.warning("Filename generation failed for '%s' in folder '%s': %s", original_filename, folder, e)
        return error_response(str(e), "filename_generation", 409)

    # Generate presigned URL for the actual upload
    result = s3_service.generate_upload_url(folder, final_filename, content_type)
    presigned_url = result['presigned_url']
    object_key = f"{folder}/{final_filename}"

    if not presigned_url:
        raise APIException(f"Failed to generate presigned URL for {object_key}")

    file.stream.seek(0)
    file_data = file.stream.read()

    upload_response = requests.put(
        presigned_url,
        data=file_data,
        headers={'Content-Type': content_type},
        timeout=60
    )

    if upload_response.status_code not in [200, 204]:
        raise APIException(f"S3 upload failed: HTTP {upload_response.status_code}")

    logger.info("Successfully uploaded file to S3: %s", object_key)

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
            logger.info("Generated download URL for newly uploaded file: %s", object_key)
        except Exception as e:
            logger.error("Failed to generate download URL for %s: %s", final_filename, e)
            uploaded_file["download_url"] = None

    return success_response(uploaded_file)