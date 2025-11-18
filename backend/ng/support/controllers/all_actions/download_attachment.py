"""
Download attachment from S3 via presigned URL redirect
"""

from flask import redirect, Response

from ....core.utils.logger import get_logger
from ....core.exceptions import NotFoundError, BusinessLogicError
from ...models import TicketAttachment
from ...services import get_support_s3_service

logger = get_logger(__name__)


def download_attachment(attachment: TicketAttachment) -> Response:
    """Redirect to presigned S3 URL for attachment download"""
    try:
        s3_service = get_support_s3_service()

        logger.info(
            "Generating presigned URL for attachment download",
            extra={
                "bucket": attachment.file_upload.bucket_name,
                "key": attachment.file_upload.s3_key,
                "attachment_id": attachment.id
            }
        )

        # Get presigned URL from service
        presigned_url = s3_service.download_ticket_attachment(
            attachment.file_upload.s3_key
        )

        if not presigned_url:
            logger.error(
                "Failed to generate presigned URL",
                extra={"attachment_id": attachment.id}
            )
            raise BusinessLogicError("Unable to generate download link")

        # Redirect to presigned URL
        return redirect(presigned_url)

    except Exception as e:
        logger.error(
            f"Error generating presigned URL for attachment: {e}",
            extra={"attachment_id": attachment.id}
        )

        if "NoSuchKey" in str(e) or "not found" in str(e).lower():
            raise NotFoundError("File not found in storage") from None
        else:
            raise BusinessLogicError("Unable to retrieve file from storage") from e