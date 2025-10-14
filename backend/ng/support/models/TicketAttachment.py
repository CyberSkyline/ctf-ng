"""
Defines the TicketAttachment model for support ticket file uploads
"""

from __future__ import annotations

from typing import Any, TypedDict
from CTFd.models import db

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator

from ..services import get_s3_upload_service


class SerializedTicketAttachment(TypedDict):
    id: int
    ticket_id: int
    s3_key: str
    bucket_name: str
    filename: str
    file_size: int
    content_type: str
    uploaded_by: int
    uploaded_at: str
    image_url: str | None


class TicketAttachment(db.Model):
    __tablename__ = "ng_ticket_attachments"

    id = db.Column(db.Integer, primary_key = True)
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_tickets.id"),
        nullable = False,
        index = True
    )
    s3_key = db.Column(
        db.String(config.TICKET_ATTACHMENT_S3_KEY_MAX_LENGTH),
        nullable = False
    )
    bucket_name = db.Column(
        db.String(config.TICKET_ATTACHMENT_BUCKET_NAME_MAX_LENGTH),
        nullable = False
    )
    filename = db.Column(
        db.String(config.TICKET_ATTACHMENT_FILENAME_MAX_LENGTH),
        nullable = False
    )
    file_size = db.Column(db.Integer, nullable = False)
    content_type = db.Column(
        db.String(config.TICKET_ATTACHMENT_CONTENT_TYPE_MAX_LENGTH),
        nullable = False
    )
    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable = False
    )
    uploaded_at = db.Column(
        db.DateTime,
        nullable = False,
        default = utc_now
    )

    ticket = db.relationship("Ticket", backref = "attachments")
    uploader = db.relationship("Users", foreign_keys = [uploaded_by])

    def __repr__(self) -> str:
        return f"<TicketAttachment {self.id} for Ticket {self.ticket_id}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate Ticket Attachment data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_model_id(
            data,
            "ticket_id",
            "Ticket",
            required = True
        )

        validator.validate_string(
            data,
            "s3_key",
            max_length = config.TICKET_ATTACHMENT_S3_KEY_MAX_LENGTH,
            required = True,
            friendly_name = "S3 key"
        )

        validator.validate_string(
            data,
            "bucket_name",
            max_length = config.TICKET_ATTACHMENT_BUCKET_NAME_MAX_LENGTH,
            required = True,
            friendly_name = "Bucket name"
        )

        validator.validate_string(
            data,
            "filename",
            max_length = config.TICKET_ATTACHMENT_FILENAME_MAX_LENGTH,
            required = True,
            friendly_name = "Filename"
        )

        validator.validate_integer(
            data,
            "file_size",
            min_value = 1,
            max_value = config.TICKET_IMAGE_MAX_SIZE,
            required = True,
            friendly_name = "File size"
        )

        validator.validate_string(
            data,
            "content_type",
            max_length = config.TICKET_ATTACHMENT_CONTENT_TYPE_MAX_LENGTH,
            required = True,
            friendly_name = "Content type"
        )

        validator.validate_model_id(
            data,
            "uploaded_by",
            "Users",
            required = True
        )

        return validator.validate()

    def serialize(
        self,
        include_admin_fields: bool = False,
        include_presigned_url: bool = True
    ) -> SerializedTicketAttachment:
        """
        Serialize attachment for API response

        Args:
            include_admin_fields: Whether to include admin only fields
        """
        data = {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "s3_key": self.s3_key,
            "bucket_name": self.bucket_name,
            "filename": self.filename,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() + "Z",
            "image_url": None,
        }

        if include_presigned_url:
            s3_service = get_s3_upload_service()
            data["image_url"] = s3_service.generate_presigned_url(
                bucket_name = self.bucket_name,
                s3_key = self.s3_key,
                expiration = config.PRESIGNED_URL_EXPIRATION_SECONDS,
            )

        return SerializedTicketAttachment(**data)

    @classmethod
    def create_attachment(
        cls,
        *,
        ticket_id: int,
        s3_key: str,
        bucket_name: str,
        filename: str,
        file_size: int,
        content_type: str,
        uploaded_by: int,
        commit: bool = True,
    ) -> TicketAttachment:
        """
        Create and persist a new ticket attachment with validation
        """
        validated_data = cls.validate(
            {
                "ticket_id": ticket_id,
                "s3_key": s3_key,
                "bucket_name": bucket_name,
                "filename": filename,
                "file_size": file_size,
                "content_type": content_type,
                "uploaded_by": uploaded_by,
            }
        )

        attachment = cls(
            ticket_id = validated_data["ticket_id"],
            s3_key = validated_data["s3_key"],
            bucket_name = validated_data["bucket_name"],
            filename = validated_data["filename"],
            file_size = validated_data["file_size"],
            content_type = validated_data["content_type"],
            uploaded_by = validated_data["uploaded_by"],
        )

        db.session.add(attachment)
        if commit:
            db.session.commit()
        return attachment

    @classmethod
    def find_by_ticket(cls, ticket_id: int) -> list[TicketAttachment]:
        """
        Get all attachments for a ticket
        """
        return cls.query.filter_by(ticket_id = ticket_id).order_by(
            cls.uploaded_at.asc()
        ).all()

    @classmethod
    def find_by_id(cls, attachment_id: int) -> TicketAttachment | None:
        """
        Find an attachment by ID
        """
        return cls.query.get(attachment_id)
