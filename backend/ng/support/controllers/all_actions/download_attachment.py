"""
Download attachment from S3 via proxy endpoint
"""

from flask import Response, current_app
import boto3
from botocore.exceptions import ClientError
from collections.abc import Generator

from .... import config
from ....core.utils.logger import get_logger
from ....core.exceptions import NotFoundError, BusinessLogicError
from ...models import TicketAttachment

logger = get_logger(__name__)


def download_attachment(
    attachment: TicketAttachment,
    chunk_size: int = config.S3_DOWNLOAD_CHUNK_SIZE
) -> Response:
    """
    Stream attachment from S3 to client via proxy.

    Args:
        attachment: TicketAttachment object with S3 location info
        chunk_size: Size of chunks to stream

    Returns:
        Flask Response with streaming content

    Raises:
        NotFoundError: If the file doesn't exist in S3
        BusinessLogicError: If S3 is not configured or other S3 errors
    """

    aws_access_key = current_app.config.get('AWS_S3_ACCESS_KEY_ID')
    aws_secret_key = current_app.config.get('AWS_S3_SECRET_ACCESS_KEY')
    aws_region = current_app.config.get('AWS_DEFAULT_REGION', 'us-east-1')

    if not aws_access_key or not aws_secret_key:
        logger.error("AWS S3 credentials not configured for download")
        raise BusinessLogicError("File storage is not configured")

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        logger.info(
            "Fetching attachment from S3",
            extra={
                "bucket": attachment.file_upload.bucket_name,
                "key": attachment.file_upload.s3_key,
                "attachment_id": attachment.id
            }
        )

        s3_response = s3_client.get_object(
            Bucket=attachment.file_upload.bucket_name,
            Key=attachment.file_upload.s3_key
        )

        def generate() -> Generator[bytes, None, None]:
            """
            Generator to stream S3 content in chunks
            """
            try:
                yield from s3_response['Body'].iter_chunks(chunk_size=chunk_size)
            except ClientError as e:
                logger.error(f"Error streaming from S3: {e}")
                return
            finally:
                s3_response['Body'].close()

        content_type = attachment.file_upload.content_type or 'application/octet-stream'
        is_image = content_type.startswith('image/')

        disposition = 'inline' if is_image else 'attachment'

        safe_filename = attachment.file_upload.filename.replace('"', '\\"').replace('\n', '').replace('\r', '')

        response = Response(
            generate(),
            mimetype=content_type,
            headers={
                'Content-Disposition': f'{disposition}; filename="{safe_filename}"',
                'Content-Length': str(attachment.file_upload.file_size),
                'Cache-Control': 'private, max-age=3600',
                'X-Content-Type-Options': 'nosniff',
            }
        )

        return response

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown') if e.response else 'Unknown'

        if error_code == 'NoSuchKey':
            logger.error(
                f"Attachment not found in S3: {attachment.file_upload.s3_key}",
                extra={"attachment_id": attachment.id}
            )
            raise NotFoundError("File not found in storage") from None

        logger.error(
            f"S3 error downloading attachment: {e}",
            extra={
                "attachment_id": attachment.id,
                "error_code": error_code
            }
        )
        raise BusinessLogicError("Unable to retrieve file from storage") from e

    except Exception as e:
        logger.error(
            f"Unexpected error downloading attachment: {e}",
            extra={"attachment_id": attachment.id}
        )
        raise BusinessLogicError("An error occurred while downloading the file") from e
