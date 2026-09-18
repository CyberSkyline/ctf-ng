"""
Download attachment from S3 via presigned URL redirect
"""

from flask import redirect, Response

from ....core.utils.logger import get_logger
from ....core.exceptions import APIException
from ...models import TicketAttachment
from ...services import get_support_s3_service

logger = get_logger(__name__)


def download_attachment(attachment: TicketAttachment) -> Response:
    """
    Redirect to presigned S3 URL for attachment download.

    No try/except here: `download_ticket_attachment` catches everything
    itself and reports anything unexpected before returning `None` - there is
    nothing left for this function to catch, so nothing to report a second
    time for the same failure.
    """
    s3_service = get_support_s3_service()

    logger.info(
        "Generating presigned URL for attachment download",
        extra={
            "bucket": attachment.file_upload.bucket_name,
            "key": attachment.file_upload.s3_key,
            "attachment_id": attachment.id
        }
    )

    presigned_url = s3_service.download_ticket_attachment(
        attachment.file_upload.s3_key
    )

    if not presigned_url:
        # Plain APIException, not BusinessLogicError: a presigned URL failing
        # is not the caller's fault, same reasoning as the S3 upload failures
        # in upload_attachment.py. Defaults to 500, reported and traced by
        # the central handler automatically.
        logger.error(
            "Failed to generate presigned URL",
            extra={"attachment_id": attachment.id}
        )
        raise APIException("Unable to generate download link")

    # Redirect to presigned URL
    return redirect(presigned_url)