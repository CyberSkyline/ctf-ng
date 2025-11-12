import boto3
import uuid
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional, Tuple
import logging
from werkzeug.datastructures import FileStorage
import os

logger = logging.getLogger(__name__)

# Global S3 service instance
_s3_service_instance = None

class S3Service:
    def __init__(self):
        self.bucket_name = None
        self.region_name = None
        self.s3_client = None
        self._is_configured = False
    
    def init_app(self, app):
        """Initialize S3 service from Flask app configuration"""
        try:
            self.bucket_name = app.config.get('AWS_S3_BUCKET_NAME')
            self.region_name = app.config.get('AWS_REGION', 'us-east-1')
            aws_access_key_id = app.config.get('AWS_ACCESS_KEY_ID')
            aws_secret_access_key = app.config.get('AWS_SECRET_ACCESS_KEY')
            
            if not all([aws_access_key_id, aws_secret_access_key, self.bucket_name]):
                logger.warning("AWS S3 configuration incomplete")
                return
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=self.region_name,
                config=boto3.session.Config(signature_version='s3v4')
            )
            
            # Test connection
            self.s3_client.list_buckets()
            self._is_configured = True
            logger.info(f"✅ S3 Service configured for bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"❌ S3 Service configuration failed: {e}")
            self._is_configured = False
    
    def is_configured(self) -> bool:
        """Check if S3 service is properly configured"""
        return self._is_configured and self.s3_client is not None
    
    # ========== PRESIGNED URL METHODS (Public Files) ==========
    
    def generate_upload_url(self, folder: str, filename: str, 
                          content_type: str = 'application/octet-stream') -> Dict[str, Any]:
        """Generate presigned URL for client-side upload (public files)"""
        if not self.is_configured():
            raise Exception("S3 service not configured")
            
        object_key = f"{folder}/{filename}"
        
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                    'ContentType': content_type,
                },
                ExpiresIn=3600,  # 1 hour
                HttpMethod='PUT'
            )
            
            logger.info(f"Generated upload URL for {object_key}")
            
            return {
                'presigned_url': presigned_url,
                'filename': filename,
                'object_key': object_key,
                'content_type': content_type
            }
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for downloads (public files)"""
        if not self.is_configured():
            raise Exception("S3 service not configured")
            
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key,
                },
                ExpiresIn=expires_in
            )
            logger.info(f"Generated download URL for {object_key}")
            return url
        except ClientError as e:
            logger.error(f"Error generating download URL: {e}")
            raise

    def search_files(self, prefix: str = '', filename_pattern: str = '', limit: int = 10) -> List[Dict[str, Any]]:
        """Search files with prefix and filename pattern matching"""
        if not self.is_configured():
            return []
        
        try:
            # List objects with the given prefix
            objects = self.list_objects(prefix=prefix)
            
            # Filter by filename pattern if provided
            if filename_pattern:
                filtered_objects = []
                for obj in objects:
                    # Extract filename from key
                    key_parts = obj['key'].split('/')
                    if len(key_parts) > 1:
                        filename = key_parts[1]
                        # Case-insensitive pattern matching
                        if filename_pattern.lower() in filename.lower():
                            filtered_objects.append(obj)
                objects = filtered_objects
            
            # Apply limit
            if limit > 0:
                objects = objects[:limit]
            
            # Format response with additional metadata
            formatted_files = []
            for obj in objects:
                key_parts = obj['key'].split('/')
                if len(key_parts) > 1:
                    formatted_files.append({
                        'key': obj['key'],
                        'filename': key_parts[1],
                        'folder': key_parts[0],
                        'size': obj['size'],
                        'last_modified': obj['last_modified'],
                        'url': self.generate_download_url(obj['key'], expires_in=3600)  # 1 hour expiry for search results
                    })
            
            return formatted_files
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    # ========== DIRECT UPLOAD METHODS (Private Ticket Attachments) ==========
    
    def upload_file_direct(self, file: FileStorage, object_key: str, 
                          content_type: str = 'application/octet-stream') -> bool:
        """Upload file directly to S3 (for ticket attachments)"""
        if not self.is_configured():
            logger.error("S3 service not configured for upload")
            return False
            
        try:
            # Reset file stream to beginning
            file.stream.seek(0)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file.stream,
                ContentType=content_type
            )
            logger.info(f"Direct upload completed for {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False
    
    def download_file_stream(self, object_key: str) -> Tuple[Any, int, str]:
        """Stream file from S3 for proxy downloads (ticket attachments)"""
        if not self.is_configured():
            raise Exception("S3 service not configured")
            
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            content_type = response.get('ContentType', 'application/octet-stream')
            content_length = response.get('ContentLength', 0)
            
            return response['Body'], content_length, content_type
            
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    # ========== COMMON METHODS ==========
    
    def list_objects(self, prefix: str = '') -> List[Dict[str, Any]]:
        """List objects in S3 bucket with prefix"""
        if not self.is_configured():
            logger.warning("S3 service not configured for list_objects")
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
            
            logger.info(f"Listed {len(files)} objects with prefix '{prefix}'")
            return files
            
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            return []
    
    def object_exists(self, object_key: str) -> bool:
        """Check if object exists in S3"""
        if not self.is_configured():
            return False
            
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False

# Global instance management
def init_s3_service() -> 'S3Service':
    """Initialize the global S3 service instance"""
    global _s3_service_instance
    _s3_service_instance = S3Service()
    return _s3_service_instance

def get_s3_service() -> S3Service:
    """Get the global S3 service instance"""
    global _s3_service_instance
    if _s3_service_instance is None:
        _s3_service_instance = S3Service()
    return _s3_service_instance