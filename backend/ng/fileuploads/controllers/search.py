"""
Cross-folder search with permission awareness
"""
from flask import jsonify, request, current_app
from ...core.services.s3_service import get_s3_service

# Add the ALLOWED_FOLDERS constant (copy from public_files.py)
ALLOWED_FOLDERS = {
    'sponsor-logos': ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'],
    'event-cards': ['image/png', 'image/jpeg', 'image/webp'],
    'favicons': ['image/x-icon', 'image/png', 'image/svg+xml']
}

def search_public_files():
    """
    Search public files across folders or within specific folder
    Supports:
    - Listing all files in a folder (just provide folder parameter)
    - Searching by filename pattern across all folders (just provide filename parameter)  
    - Searching by filename pattern within specific folder (provide both folder and filename)
    - Limiting results (limit parameter, default 10, max 50)
    """
    try:
        folder = request.args.get('folder', '').strip()
        filename_pattern = request.args.get('filename', '').strip()
        limit = min(int(request.args.get('limit', 10)), 50)  # Default 10, max 50
        
        s3_service = get_s3_service()
        if not s3_service or not s3_service.is_configured():
            return jsonify({"success": False, "error": "File storage not configured"}), 503
        
        # Case 1: List all files in a specific folder (no filename pattern)
        if folder and not filename_pattern:
            if folder not in ALLOWED_FOLDERS:
                return jsonify({"success": False, "error": f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}"}), 400
            
            prefix = f"{folder}/"
            files = s3_service.search_files(prefix=prefix, filename_pattern='', limit=limit)
            
            return jsonify({
                "success": True,
                "data": {
                    "files": files,
                    "total_count": len(files),
                    "folder": folder,
                    "search_type": "folder_listing"
                }
            })
        
        # Case 2: Search by filename pattern across all folders
        elif filename_pattern and not folder:
            all_files = []
            for public_folder in ALLOWED_FOLDERS.keys():
                prefix = f"{public_folder}/"
                folder_files = s3_service.search_files(
                    prefix=prefix, 
                    filename_pattern=filename_pattern, 
                    limit=limit
                )
                all_files.extend(folder_files)
            
            # Sort by filename and apply overall limit
            all_files.sort(key=lambda x: x['filename'])
            if limit > 0:
                all_files = all_files[:limit]
            
            return jsonify({
                "success": True,
                "data": {
                    "files": all_files,
                    "total_count": len(all_files),
                    "query": filename_pattern,
                    "folder": "all",
                    "search_type": "cross_folder_search"
                }
            })
        
        # Case 3: Search by filename pattern within specific folder
        elif folder and filename_pattern:
            if folder not in ALLOWED_FOLDERS:
                return jsonify({"success": False, "error": f"Invalid folder. Must be one of: {', '.join(ALLOWED_FOLDERS.keys())}"}), 400
            
            prefix = f"{folder}/"
            files = s3_service.search_files(
                prefix=prefix, 
                filename_pattern=filename_pattern, 
                limit=limit
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "files": files,
                    "total_count": len(files),
                    "query": filename_pattern,
                    "folder": folder,
                    "search_type": "folder_specific_search"
                }
            })
        
        # Case 4: No parameters provided - return error
        else:
            return jsonify({
                "success": False, 
                "error": "Provide either 'folder' parameter to list files in a folder, or 'filename' parameter to search across folders"
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500