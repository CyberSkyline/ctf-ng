"""
Simple FileUpload model for storing file metadata
"""

from __future__ import annotations
from typing import TypedDict

from CTFd.models import db

from ... import config
from ..utils import utc_now
from ..utils.validator import BaseValidator


class SerializedFileUpload(TypedDict):
    id: int
    s3_key: str
    bucket_name: str
    filename: str
    file_size: int
    content_type: str
    uploaded_by: int
    uploaded_at: str


class FileUpload(db.Model):
    """
    Simple model that stores file metadata and S3 location
    """
    __tablename__ = "ng_file_uploads"

    id = db.Column(db.Integer, primary_key=True)

    s3_key = db.Column(
        db.String(config.TICKET_ATTACHMENT_S3_KEY_MAX_LENGTH),
        nullable=False,
        index=True
    )
    bucket_name = db.Column(
        db.String(config.TICKET_ATTACHMENT_BUCKET_NAME_MAX_LENGTH),
        nullable=False
    )

    filename = db.Column(
        db.String(config.TICKET_ATTACHMENT_FILENAME_MAX_LENGTH),
        nullable=False
    )
    file_size = db.Column(db.Integer, nullable=False)
    content_type = db.Column(
        db.String(config.TICKET_ATTACHMENT_CONTENT_TYPE_MAX_LENGTH),
        nullable=False
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    uploaded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )

    uploader = db.relationship("Users", foreign_keys=[uploaded_by])

    def __repr__(self) -> str:
        return f"<FileUpload {self.id}: {self.filename}>"

    @classmethod
    def validate(cls, data: dict) -> dict:
        """
        Validate FileUpload data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "s3_key",
            max_length=config.TICKET_ATTACHMENT_S3_KEY_MAX_LENGTH,
            required=True,
            friendly_name="S3 key"
        )

        validator.validate_string(
            data,
            "bucket_name",
            max_length=config.TICKET_ATTACHMENT_BUCKET_NAME_MAX_LENGTH,
            required=True,
            friendly_name="Bucket name"
        )

        validator.validate_string(
            data,
            "filename",
            max_length=config.TICKET_ATTACHMENT_FILENAME_MAX_LENGTH,
            required=True,
            friendly_name="Filename"
        )

        validator.validate_integer(
            data,
            "file_size",
            min_value=1,
            max_value=config.TICKET_ATTACHMENT_MAX_SIZE,
            required=True,
            friendly_name="File size"
        )

        validator.validate_string(
            data,
            "content_type",
            max_length=config.TICKET_ATTACHMENT_CONTENT_TYPE_MAX_LENGTH,
            required=True,
            friendly_name="Content type"
        )

        validator.validate_model_id(
            data,
            "uploaded_by",
            "Users",
            required=True
        )

        return validator.validate()

    def serialize(self, include_admin_fields: bool = False) -> SerializedFileUpload:
        """
        Serialize file upload for API response
        """
        data = {
            "id": self.id,
            "s3_key": self.s3_key,
            "bucket_name": self.bucket_name,
            "filename": self.filename,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() + "Z",
        }

        return SerializedFileUpload(**data)

    @classmethod
    def create_file_upload(
        cls,
        *,
        s3_key: str,
        bucket_name: str,
        filename: str,
        file_size: int,
        content_type: str,
        uploaded_by: int,
        commit: bool = True,
    ) -> FileUpload:
        """
        Create and persist a new file upload with validation
        """
        validated_data = cls.validate(
            {
                "s3_key": s3_key,
                "bucket_name": bucket_name,
                "filename": filename,
                "file_size": file_size,
                "content_type": content_type,
                "uploaded_by": uploaded_by,
            }
        )

        file_upload = cls(
            s3_key=validated_data["s3_key"],
            bucket_name=validated_data["bucket_name"],
            filename=validated_data["filename"],
            file_size=validated_data["file_size"],
            content_type=validated_data["content_type"],
            uploaded_by=validated_data["uploaded_by"],
        )

        db.session.add(file_upload)
        if commit:
            db.session.commit()
        return file_upload

    @classmethod
    def find_by_id(cls, file_id: int) -> FileUpload | None:
        """
        Find a file upload by ID
        """
        return cls.query.get(file_id)
