"""
AWS S3 Upload Service for support ticket images
"""

import uuid
import boto3
from typing import Any
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    BotoCoreError,
)
from flask import current_app
from werkzeug.datastructures import FileStorage

from ... import config
from ...core.utils.logger import get_logger


logger = get_logger(__name__)


class AWSS3UploadService:
    """
    Service for uploading files to AWS S3
    """
    def __init__(self):
        self.s3_client: Any | None = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize AWS S3 client if credentials are configured
        """
        try:
            aws_access_key = current_app.config.get(
                'AWS_S3_ACCESS_KEY_ID'
            )
            aws_secret_key = current_app.config.get(
                'AWS_S3_SECRET_ACCESS_KEY'
            )
            aws_region = current_app.config.get(
                'AWS_DEFAULT_REGION',
                'us-east-1'
            )

            if not aws_access_key or not aws_secret_key:
                logger.debug(
                    "AWS S3 credentials not configured - file uploads disabled"
                )
                return

            self.s3_client = boto3.client(
                's3',
                aws_access_key_id = aws_access_key,
                aws_secret_access_key = aws_secret_key,
                region_name = aws_region
            )

            logger.info("AWS S3 client initialized successfully")

        except NoCredentialsError:
            logger.debug(
                "AWS credentials not found - file uploads disabled"
            )
        except ClientError as e:
            logger.error("Failed to initialize AWS S3 client: %s", e)
        except (BotoCoreError) as e:
            logger.error("AWS connection error initializing S3: %s", e)
        except Exception as e:
            logger.error("Unexpected error initializing AWS S3: %s", e)

    def is_configured(self) -> bool:
        """
        Check if AWS S3 is properly configured
        """
        return self.s3_client is not None

    def upload_ticket_image(
        self,
        file: FileStorage,
        ticket_id: int,
        file_extension: str,
    ) -> dict[str,
              Any] | None:
        """
        Upload ticket image to S3
        (validation in controller)

        Args:
            file: File to upload
            ticket_id: Ticket ID for organizing uploads
            file_extension: File extension without dot (e.g., 'webp', 'png')

        Returns:
            dict with s3_key, bucket_name, file_size, or None on failure
        """
        if not self.is_configured():
            logger.debug("AWS S3 not configured - cannot upload file")
            return None

        bucket_name = current_app.config.get('AWS_S3_BUCKET_NAME')
        if not bucket_name:
            logger.error("No S3 bucket configured")
            return None

        try:
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

            content_type = f"image/{file_extension}"
            unique_id = str(uuid.uuid4())
            s3_key = f"{config.S3_TICKET_ATTACHMENTS_PREFIX}/{ticket_id}/{unique_id}.{file_extension}"

            if self.s3_client is None:
                logger.error("S3 client is None")
                return None

            self.s3_client.upload_fileobj(
                file,
                bucket_name,
                s3_key,
                ExtraArgs = {
                    'ContentType': content_type,
                }
            )

            logger.info(
                "File uploaded successfully to s3://%s/%s",
                bucket_name,
                s3_key
            )

            return {
                's3_key': s3_key,
                'bucket_name': bucket_name,
                'file_size': file_size,
            }

        except ClientError as e:
            logger.error("AWS S3 error uploading file: %s", e)
            return None
        except Exception as e:
            logger.error("Unexpected error uploading file: %s", e)
            return None

    def generate_presigned_url(
        self,
        bucket_name: str,
        s3_key: str,
        expiration: int | None = None,
    ) -> str | None:
        """
        Generate a presigned URL for viewing an S3 object

        Args:
            bucket_name: S3 bucket name
            s3_key: S3 object key
            expiration: URL expiration time in seconds (defaults to config constant)

        Returns:
            Presigned URL string or None on failure
        """
        if expiration is None:
            expiration = config.PRESIGNED_URL_EXPIRATION_SECONDS
        if not self.is_configured():
            logger.debug(
                "AWS S3 not configured - cannot generate presigned URL"
            )
            return None

        if self.s3_client is None:
            logger.error("S3 client is None")
            return None

        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params = {
                    'Bucket': bucket_name,
                    'Key': s3_key,
                },
                ExpiresIn = expiration
            )
            return presigned_url

        except ClientError as e:
            logger.error("Error generating presigned URL: %s", e)
            return None
        except Exception as e:
            logger.error(
                "Unexpected error generating presigned URL: %s",
                e
            )
            return None


_s3_upload_service: AWSS3UploadService | None = None


def get_s3_upload_service() -> AWSS3UploadService:
    """
    Get the global S3 upload service instance
    """
    global _s3_upload_service
    if _s3_upload_service is None:
        _s3_upload_service = AWSS3UploadService()
    return _s3_upload_service
