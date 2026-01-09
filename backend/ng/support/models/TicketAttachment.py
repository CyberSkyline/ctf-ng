"""
Defines the TicketAttachment model
"""

from __future__ import annotations

from typing import Any, TypedDict

from CTFd.models import db
from flask import current_app

from ... import config
from ...core.models.FileUpload import FileUpload
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator


class SerializedTicketAttachment(TypedDict):
    id: int
    ticket_id: int
    file_upload_id: int
    filename: str
    file_size: int
    content_type: str
    uploaded_by: int
    uploaded_at: str
    download_url: str


class TicketAttachment(db.Model):
    """
    Junction table linking tickets to file uploads
    """
    __tablename__ = "ng_ticket_attachments"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_tickets.id"),
        nullable=False,
        index=True
    )
    file_upload_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_file_uploads.id"),
        nullable=False,
        index=True
    )
    attached_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )

    ticket = db.relationship("Ticket", backref="attachments")
    file_upload = db.relationship("FileUpload", backref="ticket_attachments")

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
            required=True
        )

        validator.validate_model_id(
            data,
            "file_upload_id",
            "FileUpload",
            required=True
        )

        return validator.validate()

    def serialize(
        self,
        include_admin_fields: bool = False
    ) -> SerializedTicketAttachment:
        """
        Serialize attachment for API response

        Args:
            include_admin_fields: Whether to include admin only fields
        """
        if not self.file_upload:
            raise ValueError("FileUpload not loaded for TicketAttachment")

        route_prefix = current_app.config.get('ROUTE_PREFIX') or ''
        download_path = f"{route_prefix}{config.TICKET_ATTACHMENT_DOWNLOAD_PATH}"

        data = {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "file_upload_id": self.file_upload_id,
            "filename": self.file_upload.filename,
            "file_size": self.file_upload.file_size,
            "content_type": self.file_upload.content_type,
            "uploaded_by": self.file_upload.uploaded_by,
            "uploaded_at": self.file_upload.uploaded_at.isoformat() + "Z",
            "download_url": f"{download_path}/{self.id}",
        }

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
        Create and persist a new ticket attachment with its file upload
        """
        file_upload = FileUpload.create_file_upload(
            s3_key=s3_key,
            bucket_name=bucket_name,
            filename=filename,
            file_size=file_size,
            content_type=content_type,
            uploaded_by=uploaded_by,
            commit=False,
        )

        db.session.add(file_upload)
        db.session.flush()

        validated_data = cls.validate(
            {
                "ticket_id": ticket_id,
                "file_upload_id": file_upload.id,
            }
        )

        attachment = cls(
            ticket_id=validated_data["ticket_id"],
            file_upload_id=validated_data["file_upload_id"],
        )

        attachment.file_upload = file_upload

        db.session.add(attachment)
        if commit:
            db.session.commit()
        return attachment

    @classmethod
    def find_by_ticket(cls, ticket_id: int) -> list[TicketAttachment]:
        """
        Get all attachments for a ticket
        """
        return cls.query.filter_by(ticket_id=ticket_id).order_by(
            cls.attached_at.asc()
        ).all()

    @classmethod
    def find_by_id(cls, attachment_id: int) -> TicketAttachment | None:
        """
        Find an attachment by ID
        """
        return cls.query.get(attachment_id)


