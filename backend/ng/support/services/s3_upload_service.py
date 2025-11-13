"""
Support-specific file operations using shared core S3 service
Private ticket attachments with proxy download
"""
import uuid
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from flask import current_app
from ...core.utils.file_helpers import get_file_size


class SupportS3Service:
    """
    Thin wrapper around shared S3 service for support ticket attachments
    Uses direct uploads and proxy downloads for privacy
    """
    
    def __init__(self):
        self.s3_service = None
    
    def _get_s3_service(self):
        """Get shared S3 service instance"""
        if self.s3_service is None:
            from ...core.services.s3_service import get_s3_service
            self.s3_service = get_s3_service()
        return self.s3_service
    
    def upload_ticket_attachment(self, file: FileStorage, ticket_id: int, 
                               file_extension: str = None) -> Optional[Dict[str, Any]]:
        """
        Upload ticket attachment directly to S3 (private)
        
        Returns file metadata for database storage
        """
        s3_service = self._get_s3_service()
        
        if not s3_service or not s3_service.is_configured():
            current_app.logger.error("S3 not configured for ticket attachment upload")
            return None
        
        try:
            # Get file info
            file_size = get_file_size(file)
            content_type = file.content_type or 'application/octet-stream'
            
            # Use provided extension or detect from content type
            if file_extension:
                actual_extension = file_extension
            else:
                actual_extension = self._get_extension_from_content_type(content_type)
            
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.{actual_extension}"
            object_key = f"support-tickets/{ticket_id}/{filename}"
            
            # Upload using shared service
            success = s3_service.upload_file_direct(file, object_key, content_type)
            
            if success:
                return {
                    's3_key': object_key,
                    'bucket_name': s3_service.bucket_name,
                    'file_size': file_size,
                    'filename': file.filename,  # Original filename
                    'content_type': content_type
                }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Ticket attachment upload error: {e}")
            return None
    
    def download_ticket_attachment(self, s3_key: str):
        """
        Stream ticket attachment for proxy download
        Returns (stream, content_length, content_type)
        """
        s3_service = self._get_s3_service()
        if not s3_service or not s3_service.is_configured():
            raise Exception("S3 service not configured")
        
        return s3_service.download_file_stream(s3_key)
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
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

# Global instance
_support_s3_service: Optional[SupportS3Service] = None

def get_support_s3_service() -> SupportS3Service:
    global _support_s3_service
    if _support_s3_service is None:
        _support_s3_service = SupportS3Service()
    return _support_s3_service

def get_s3_upload_service() -> SupportS3Service:
    """Alias for get_support_s3_service to match existing imports"""
    return get_support_s3_service()