"""
AWS S3 Upload Service for support ticket images
(and MinIO for development)
"""

import uuid
import boto3
from enum import Enum
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
from ...core.utils.file_helpers import get_file_size


logger = get_logger(__name__)


class StorageType(Enum):
    """
    Enum for different storage backend types
    """
    UNCONFIGURED = "unconfigured"
    AWS = "aws"
    MINIO = "minio"


class AWSS3UploadService:
    """
    Service for uploading files to AWS S3 or S3 compatible storage (MinIO)
    """
    def __init__(self):
        self.s3_client: Any | None = None
        self.storage_type: StorageType = StorageType.UNCONFIGURED
        self.bucket_name: str | None = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize S3 client (AWS S3 or MinIO) based on USE_MINIO flag
        Falls back gracefully if neither is configured
        """
        try:
            use_minio = current_app.config.get('USE_MINIO',
                                               'false').lower() == 'true'

            if use_minio:
                access_key = current_app.config.get('MINIO_ACCESS_KEY')
                secret_key = current_app.config.get('MINIO_SECRET_KEY')
                endpoint_url = current_app.config.get('MINIO_ENDPOINT')
                self.bucket_name = current_app.config.get('MINIO_BUCKET')

                if not access_key or not secret_key or not endpoint_url:
                    logger.debug(
                        "MinIO credentials not fully configured - checking AWS"
                    )
                    use_minio = False
                else:
                    # Prod setup wont have MinIO configured
                    self.s3_client = boto3.client(
                        's3',
                        aws_access_key_id = access_key,
                        aws_secret_access_key = secret_key,
                        endpoint_url = endpoint_url,
                        region_name = 'us-east-1'  # MinIO doesn't care about region but boto3 needs it
                    )
                    self.storage_type = StorageType.MINIO
                    logger.info(
                        f"MinIO client initialized at {endpoint_url}"
                    )
                    return

            if not use_minio:
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
                self.bucket_name = current_app.config.get(
                    'AWS_S3_BUCKET_NAME'
                )

                if not aws_access_key or not aws_secret_key:
                    logger.debug(
                        "No storage credentials configured - file uploads disabled"
                    )
                    return

                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id = aws_access_key,
                    aws_secret_access_key = aws_secret_key,
                    region_name = aws_region
                )
                self.storage_type = StorageType.AWS
                logger.info("AWS S3 client initialized successfully")

        except NoCredentialsError:
            logger.debug(
                "Storage credentials not found - file uploads disabled"
            )
        except ClientError as e:
            logger.error(
                f"Failed to initialize {self.storage_type.value} client: %s",
                e
            )
        except BotoCoreError as e:
            logger.error(
                f"Connection error initializing {self.storage_type.value}: %s",
                e
            )
        except Exception as e:
            logger.error("Unexpected error initializing storage: %s", e)

    def is_configured(self) -> bool:
        """
        Check if S3 storage is properly configured
        """
        return self.s3_client is not None and self.bucket_name is not None

    def get_storage_type(self) -> str:
        """
        Get the current storage type: 'aws', 'minio', or 'unconfigured'
        """
        return self.storage_type.value

    def upload_ticket_attachment(
        self,
        file: FileStorage,
        ticket_id: int,
        file_extension: str,
    ) -> dict[str,
              Any] | None:
        """
        Upload ticket attachment to S3
        (validation in controller)

        Args:
            file: File to upload
            ticket_id: Ticket ID for organizing uploads
            file_extension: File extension without dot (e.g., 'webp', 'png')

        Returns:
            dict with s3_key, bucket_name, file_size, or None on failure
        """
        if not self.is_configured():
            logger.debug(
                f"Storage not configured ({self.storage_type.value}) - cannot upload file"
            )
            return None

        if not self.bucket_name:
            logger.error("No bucket configured")
            return None

        try:
            file_size = get_file_size(file)
            file.seek(0)

            content_type = f"image/{file_extension}"
            unique_id = str(uuid.uuid4())
            s3_key = f"{config.S3_TICKET_ATTACHMENTS_PREFIX}/{ticket_id}/{unique_id}.{file_extension}"

            if self.s3_client is None:
                logger.error("S3 client is None")
                return None

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs = {
                    'ContentType': content_type,
                }
            )

            logger.info(
                "File uploaded successfully to %s (s3://%s/%s)",
                self.storage_type.value,
                self.bucket_name,
                s3_key
            )

            return {
                's3_key': s3_key,
                'bucket_name': self.bucket_name,
                'file_size': file_size,
            }

        except ClientError as e:
            logger.error(
                f"{self.storage_type.value} error uploading file: %s",
                e
            )
            return None
        except Exception as e:
            logger.error("Unexpected error uploading file: %s", e)
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
