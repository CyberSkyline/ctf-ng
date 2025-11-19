"""
Support-specific file operations using shared core S3 service
Private ticket attachments with proxy download
"""
import uuid
from flask import current_app
from ... import config
from ...core.exceptions import ValidationError
from ..models import TicketAttachment


class SupportS3Service:
    """S3 service for support ticket attachments"""

    def __init__(self):
        self.s3_service = None

    def _get_s3_service(self):
        if self.s3_service is None:
            from ...core.services.s3_service import get_s3_service
            self.s3_service = get_s3_service()
        return self.s3_service

    def is_configured(self) -> bool:
        s3_service = self._get_s3_service()
        return self.s3_service is not None and s3_service.is_configured()

    def upload_file_direct(self, ticket_id: int, file_data: bytes, filename: str,
                          content_type: str, uploaded_by: int) -> TicketAttachment | None:
        """Upload file to S3 and create database record"""
        from ..models import TicketAttachment
        import requests

        s3_service = self._get_s3_service()

        if not s3_service or not s3_service.is_configured():
            current_app.logger.error("S3 not configured for ticket attachment upload")
            return None

        try:
            file_extension = self._get_extension_from_content_type(content_type)
            unique_id = str(uuid.uuid4())
            generated_filename = f"{unique_id}.{file_extension}"
            object_key = f"support-tickets/{ticket_id}/{generated_filename}"

            result = s3_service.generate_upload_url(f"support-tickets/{ticket_id}", generated_filename, content_type)

            response = requests.put(
                result['presigned_url'],
                data=file_data,
                headers={'Content-Type': content_type}
            )

            if response.status_code != 200:
                current_app.logger.error(f"S3 upload failed: {response.status_code} - {response.text}")
                return None

            attachment = TicketAttachment.create_attachment(
                ticket_id=ticket_id,
                s3_key=object_key,
                bucket_name=s3_service.bucket_name,
                filename=filename,
                file_size=len(file_data),
                content_type=content_type,
                uploaded_by=uploaded_by,
            )

            current_app.logger.info(f"Direct upload successful for ticket {ticket_id}, attachment {attachment.id}")
            return attachment

        except Exception as e:
            current_app.logger.error(f"Direct upload failed: {e}")
            return None

    def confirm_upload_and_create_attachment(
        self,
        ticket_id: int,
        object_key: str,
        filename: str,
        original_filename: str,
        content_type: str,
        file_size: int,
        uploaded_by: int
    ) -> 'TicketAttachment':
        """Validate upload and create attachment record"""
        from ..models import TicketAttachment

        if not all([object_key, filename, original_filename, content_type]):
            raise ValidationError(
                "Missing required fields",
                errors={
                    "object_key": "S3 object key is required",
                    "filename": "Generated filename is required",
                    "original_filename": "Original filename is required",
                    "content_type": "Content type is required"
                }
            )

        if not file_size or file_size <= 0:
            raise ValidationError("Invalid file size", errors={"file_size": "File size must be positive"})

        if file_size > config.TICKET_ATTACHMENT_MAX_SIZE:
            max_mb = config.TICKET_ATTACHMENT_MAX_SIZE / (1024 * 1024)
            raise ValidationError(
                f"File size exceeds maximum of {max_mb}MB",
                errors={"file_size": f"File must be smaller than {max_mb}MB"}
            )

        expected_prefix = f"support-tickets/{ticket_id}/"
        if not object_key.startswith(expected_prefix):
            raise ValidationError("Invalid object key", errors={"object_key": "Object key does not match ticket"})

        s3_service = self._get_s3_service()
        if not s3_service or not s3_service.is_configured():
            raise ValidationError("File storage not configured", errors={}, status_code=503)

        if not s3_service.object_exists(object_key):
            raise ValidationError("File not found in storage", errors={"object_key": "Uploaded file not found"})

        attachment = TicketAttachment.create_attachment(
            ticket_id=ticket_id,
            s3_key=object_key,
            bucket_name=s3_service.bucket_name,
            filename=original_filename,
            file_size=file_size,
            content_type=content_type,
            uploaded_by=uploaded_by,
        )

        current_app.logger.info(f"Confirmed upload and created attachment {attachment.id} for ticket {ticket_id}")
        return attachment

    def download_ticket_attachment(self, s3_key: str) -> str | None:
        """Generate presigned download URL"""
        s3_service = self._get_s3_service()
        if not s3_service or not s3_service.is_configured():
            current_app.logger.error("S3 service not configured")
            return None

        try:
            presigned_url = s3_service.generate_download_url(
                s3_key,
                expires_in=3600  # 1 hour
            )
            return presigned_url
        except Exception as e:
            current_app.logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            return None

    def _get_extension_from_content_type(self, content_type: str) -> str:
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

_support_s3_service: SupportS3Service | None = None

def get_support_s3_service() -> SupportS3Service:
    global _support_s3_service
    if _support_s3_service is None:
        _support_s3_service = SupportS3Service()
    return _support_s3_service

def get_s3_upload_service() -> SupportS3Service:
    return get_support_s3_service()