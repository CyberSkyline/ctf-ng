"""
AWS SES Email Service for support ticket notifications
"""

from typing import Any

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
)
from flask import current_app

from ...core.utils.logger import get_logger

logger = get_logger(__name__)


class AWSEmailService:
    """
    Service for sending emails via AWS SES
    """

    def __init__(self):
        self.ses_client: Any | None = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize AWS SES client if credentials are configured
        """
        try:
            aws_access_key = current_app.config.get("AWS_ACCESS_KEY_ID")
            aws_secret_key = current_app.config.get("AWS_SECRET_ACCESS_KEY")
            aws_region = current_app.config.get("AWS_DEFAULT_REGION", "us-east-1")

            if not aws_access_key or not aws_secret_key:
                logger.debug("AWS SES credentials not configured - email notifications disabled")
                return

            self.ses_client = boto3.client(
                "ses", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region
            )

            self.ses_client.get_send_quota()
            logger.info("AWS SES client initialized successfully")

        except NoCredentialsError:
            logger.debug("AWS credentials not found - email notifications disabled")
        except ClientError as e:
            logger.error("Failed to initialize AWS SES client: %s", e)
        except (BotoCoreError, EndpointConnectionError) as e:
            logger.error("AWS connection error initializing SES: %s", e)
        except Exception as e:
            logger.error("Unexpected error initializing AWS SES: %s", e)

    def is_configured(self) -> bool:
        """
        Check if AWS SES is properly configured
        """
        return self.ses_client is not None

    def send_email(
        self, *, to_emails: list[str], subject: str, html_body: str, text_body: str, from_email: str | None = None
    ) -> bool:
        """
        Send email via AWS SES

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body
            from_email: From email address
        """
        if not self.is_configured():
            logger.debug("AWS SES not configured - would send email: %s to %s", subject, to_emails)
            return False

        if not to_emails:
            logger.warning("No recipient emails provided")
            return False

        try:
            from_email = from_email or current_app.config.get("AWS_SES_FROM_EMAIL")
            if not from_email:
                logger.error("No from email configured for AWS SES")
                return False

            if self.ses_client is None:
                logger.error("SES client is None")
                return False

            response = self.ses_client.send_email(
                Source=from_email,
                Destination={
                    "ToAddresses": to_emails,
                },
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                    },
                },
            )

            message_id = response.get("MessageId")
            logger.info("Email sent successfully to %s, MessageId: %s", to_emails, message_id)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("AWS SES error sending email: %s - %s", error_code, e)
            return False
        except (BotoCoreError, EndpointConnectionError) as e:
            logger.error("AWS connection error sending email: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending email: %s", e)
            return False


_email_service: AWSEmailService | None = None


def get_email_service() -> AWSEmailService:
    """
    Get the global email service instance
    """
    global _email_service
    if _email_service is None:
        _email_service = AWSEmailService()
    return _email_service
