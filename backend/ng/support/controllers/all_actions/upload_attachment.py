"""
Direct ticket attachment upload controller and function
Handles server-side upload to S3 using presigned URLs behind the scenes
"""

import uuid
import requests
from flask import current_app, request
from flask_restx import Resource
from werkzeug.datastructures import FileStorage

from .... import config
from ....core.utils.file_helpers import (
    get_file_size,
    validate_image_content
)
from ....core.exceptions import ValidationError
from ....core.utils import success_response

from ...models import Ticket, TicketAttachment
from ...services.s3_upload_service import SupportS3Service
from ...services import get_s3_upload_service


class UploadAttachment(Resource):
    """Direct ticket attachment upload - server handles S3 upload"""

    def handle_direct_upload(self, ticket_id: int, user_id: int, ticket: Ticket = None):
        """
        Direct upload attachment to ticket
        """
        if not ticket:
            ticket = Ticket.find_by_id(ticket_id)
            if not ticket:
                return {"error": "Ticket not found"}, 404

        if ticket.status == "closed":
            return {"error": "Ticket is closed"}, 400

        service = SupportS3Service()
        return self._handle_direct_upload(ticket_id, user_id, service)

    def _handle_direct_upload(self, ticket_id: int, user_id: int, service: SupportS3Service):
        """Handle direct file upload with server-side S3 upload"""

        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file: FileStorage = request.files['file']
        if not file or file.filename == '':
            return {"error": "No file selected"}, 400

        if not file.content_type:
            return {"error": "File content type required"}, 400

        if file.content_type not in config.TICKET_ATTACHMENT_ALLOWED_TYPES:
            allowed_types_str = ', '.join(config.TICKET_ATTACHMENT_ALLOWED_TYPES)
            return {"error": f"File type {file.content_type} not allowed. Allowed types: {allowed_types_str}"}, 400

        file_data = file.read()
        file_size = len(file_data)

        if file_size > config.TICKET_ATTACHMENT_MAX_SIZE:
            return {"error": f"File too large. Max size: {config.TICKET_ATTACHMENT_MAX_SIZE} bytes"}, 400

        try:
            attachment = service.upload_file_direct(
                ticket_id=ticket_id,
                file_data=file_data,
                filename=file.filename,
                content_type=file.content_type,
                uploaded_by=user_id
            )

            if not attachment:
                return {"error": "Failed to upload file"}, 500

            return success_response({
                "message": "File uploaded successfully",
                "attachment_id": attachment.id,
                "filename": file.filename,
                "file_size": file_size
            }, status_code=201)

        except Exception as e:
            current_app.logger.error(f"Direct upload failed: {e}")
            return {"error": "Upload failed"}, 500


def upload_attachment(file: FileStorage, ticket: Ticket, uploaded_by: int) -> TicketAttachment:
    """Upload attachment directly to S3 using server-side presigned URL generation"""

    if not file or not file.filename:
        raise ValidationError("No file provided")

    if ticket.status == "closed":
        raise ValidationError(
            "Ticket is closed",
            errors={"ticket": "Ticket is closed"},
        )

    file_size = get_file_size(file)

    if file_size > config.TICKET_ATTACHMENT_MAX_SIZE:
        max_mb = config.TICKET_ATTACHMENT_MAX_SIZE / (1024 * 1024)
        raise ValidationError(
            f"File size exceeds maximum of {max_mb}MB",
            errors={"file": f"File must be smaller than {max_mb}MB"}
        )

    try:
        image_format, content_type = validate_image_content(file)
    except ValueError as e:
        raise ValidationError(
            str(e),
            errors={"file": "File must be a valid image"}
        ) from e

    if content_type not in config.TICKET_ATTACHMENT_ALLOWED_TYPES:
        allowed_types_str = ', '.join(config.TICKET_ATTACHMENT_ALLOWED_TYPES)
        raise ValidationError(
            f"Only {allowed_types_str} images are allowed",
            errors={"file": f"File must be in one of these formats: {allowed_types_str}"}
        )

    s3_service = get_s3_upload_service()
    if not s3_service or not s3_service.is_configured():
        raise ValidationError("File storage not configured", errors={})

    try:
        folder = f"support-tickets/{ticket.id}"
        filename = f"{uuid.uuid4()}.{image_format}"
        presigned_response = s3_service._get_s3_service().generate_upload_url(folder, filename, content_type)

        if not presigned_response:
            raise ValidationError("Failed to generate presigned URL", errors={})

        presigned_url = presigned_response.get('presigned_url')
        object_key = presigned_response.get('object_key')

        if not presigned_url:
            raise ValidationError("Failed to generate presigned URL", errors={})

        if not presigned_url:
            raise ValidationError("Failed to generate presigned URL", errors={})

        file.stream.seek(0)
        file_data = file.stream.read()
        actual_file_size = len(file_data)

        upload_response = requests.put(
            presigned_url,
            data=file_data,
            headers={'Content-Type': content_type},
            timeout=60
        )

        if upload_response.status_code not in [200, 204]:
            current_app.logger.error(f"S3 upload failed: HTTP {upload_response.status_code}")
            raise ValidationError("Failed to upload file to S3", errors={})

        core_s3_service = s3_service._get_s3_service()

        attachment = TicketAttachment.create_attachment(
            ticket_id=ticket.id,
            s3_key=object_key,
            bucket_name=core_s3_service.bucket_name,
            filename=file.filename,
            file_size=actual_file_size,
            content_type=content_type,
            uploaded_by=uploaded_by,
        )

        return attachment

    except requests.RequestException as e:
        current_app.logger.error(f"S3 upload request error: {e}")
        raise ValidationError("Failed to upload file to S3", errors={}) from e
    except Exception as e:
        current_app.logger.error(f"Ticket attachment upload error: {e}")
        raise ValidationError("Upload failed", errors={}) from e