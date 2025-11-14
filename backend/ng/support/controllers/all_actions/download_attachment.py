"""
Download attachment from S3 via proxy endpoint
"""

from flask import Response
from collections.abc import Generator

from .... import config
from ....core.utils.logger import get_logger
from ....core.exceptions import NotFoundError, BusinessLogicError
from ...models import TicketAttachment
from ...services import get_support_s3_service

logger = get_logger(__name__)


def download_attachment(attachment: TicketAttachment) -> Response:
    """
    Stream attachment from S3 to client via proxy using shared service.

    Args:
        attachment: TicketAttachment object with S3 location info

    Returns:
        Flask Response with streaming content

    Raises:
        NotFoundError: If the file doesn't exist in S3
        BusinessLogicError: If S3 is not configured or other S3 errors
    """
    try:
        s3_service = get_support_s3_service()

        logger.info(
            "Fetching attachment from S3 via shared service",
            extra={
                "bucket": attachment.file_upload.bucket_name,
                "key": attachment.file_upload.s3_key,
                "attachment_id": attachment.id
            }
        )

        # Use shared service for streaming
        stream, content_length, content_type = s3_service.download_ticket_attachment(
            attachment.file_upload.s3_key
        )

        def generate() -> Generator[bytes, None, None]:
            """
            Generator to stream S3 content in chunks
            """
            try:
                chunk_size = config.S3_DOWNLOAD_CHUNK_SIZE
                while True:
                    chunk = stream.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            except Exception as e:
                logger.error(f"Error streaming from S3: {e}")
                return
            finally:
                stream.close()

        is_image = content_type.startswith('image/')
        disposition = 'inline' if is_image else 'attachment'

        safe_filename = attachment.file_upload.filename.replace('"', '\\"').replace('\n', '').replace('\r', '')

        response = Response(
            generate(),
            mimetype=content_type,
            headers={
                'Content-Disposition': f'{disposition}; filename="{safe_filename}"',
                'Content-Length': str(content_length),
                'Cache-Control': 'private, max-age=3600',
                'X-Content-Type-Options': 'nosniff',
            }
        )

        return response

    except Exception as e:
        logger.error(
            f"Error downloading attachment via shared service: {e}",
            extra={"attachment_id": attachment.id}
        )

        if "NoSuchKey" in str(e) or "not found" in str(e).lower():
            raise NotFoundError("File not found in storage") from None
        else:
            raise BusinessLogicError("Unable to retrieve file from storage") from e