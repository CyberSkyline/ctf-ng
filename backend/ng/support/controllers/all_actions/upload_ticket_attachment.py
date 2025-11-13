"""
Upload attachment for support ticket
"""

from werkzeug.datastructures import FileStorage

from .... import config
from ....core.utils.file_helpers import (
    get_file_size,
    validate_image_content
)
from ....core.exceptions import ValidationError

from ...models import Ticket, TicketAttachment
from ...services import get_s3_upload_service



def upload_ticket_attachment(
    file: FileStorage,
    ticket: Ticket,
    uploaded_by: int,
) -> TicketAttachment:
    """
    Upload an attachment for a support ticket

    Args:
        file: File to upload
        ticket: Ticket to attach file to
        uploaded_by: User ID of uploader

    Returns:
        TicketAttachment with presigned URL
    """
    if not file or not file.filename:
        raise ValidationError("No file provided")

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

    if image_format not in config.TICKET_ATTACHMENT_ALLOWED_TYPES:
        allowed_types_str = ', '.join(f".{t}" for t in config.TICKET_ATTACHMENT_ALLOWED_TYPES)
        raise ValidationError(
            f"Only {allowed_types_str} images are allowed",
            errors={"file": f"File must be in one of these formats: {allowed_types_str}"}
        )

    s3_service = get_s3_upload_service()
    upload_result = s3_service.upload_ticket_attachment(
        file=file,
        ticket_id=ticket.id,
        file_extension=image_format,
    )

    if not upload_result:
        raise ValidationError(
            "Failed to upload file. Please try again.",
            errors={"file": "Upload failed"}
        )

    attachment = TicketAttachment.create_attachment(
        ticket_id=ticket.id,
        s3_key=upload_result['s3_key'],
        bucket_name=upload_result['bucket_name'],
        filename=file.filename,
        file_size=upload_result['file_size'],
        content_type=content_type,
        uploaded_by=uploaded_by,
    )

    return attachment
