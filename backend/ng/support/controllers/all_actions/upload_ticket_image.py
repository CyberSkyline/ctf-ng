"""
Upload image for support ticket
"""

from werkzeug.datastructures import FileStorage

from .... import config
from ....core.exceptions import ValidationError

from ...models import Ticket, TicketAttachment
from ...services import get_s3_upload_service



def upload_ticket_image(
    file: FileStorage,
    ticket: Ticket,
    uploaded_by: int,
) -> TicketAttachment:
    """
    Upload an image for a support ticket

    Args:
        file: Image file to upload
        ticket: Ticket to attach image to
        uploaded_by: User ID of uploader

    Returns:
        TicketAttachment with presigned URL
    """
    if not file or not file.filename:
        raise ValidationError("No file provided")

    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if file_ext not in config.TICKET_IMAGE_ALLOWED_TYPES:
        allowed_types_str = ', '.join(f".{t}" for t in config.TICKET_IMAGE_ALLOWED_TYPES)
        raise ValidationError(
            f"Only {allowed_types_str} files are allowed",
            errors={"file": f"File must be in one of these formats: {allowed_types_str}"}
        )

    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > config.TICKET_IMAGE_MAX_SIZE:
        max_mb = config.TICKET_IMAGE_MAX_SIZE / (1024 * 1024)
        raise ValidationError(
            f"File size exceeds maximum of {max_mb}MB",
            errors={"file": f"File must be smaller than {max_mb}MB"}
        )

    s3_service = get_s3_upload_service()
    upload_result = s3_service.upload_ticket_image(
        file=file,
        ticket_id=ticket.id,
        file_extension=file_ext,
    )

    if not upload_result:
        raise ValidationError(
            "Failed to upload image. Please try again.",
            errors={"file": "Upload failed"}
        )

    content_type = f"image/{file_ext}"

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
