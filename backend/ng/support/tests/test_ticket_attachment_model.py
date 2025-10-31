"""
Model tests for TicketAttachment
"""

import pytest
from unittest.mock import MagicMock, patch

from ... import config
from ...core.exceptions import ValidationError
from ..models import TicketAttachment


class TestTicketAttachment:
    def test_repr(self, db_session, ticket, user):
        """
        Test the string representation of the model
        """
        attachment = TicketAttachment.create_attachment(
            ticket_id = ticket.id,
            s3_key = "support-tickets/1/test-uuid.webp",
            bucket_name = "test-bucket",
            filename = "test-image.webp",
            file_size = 1024,
            content_type = "image/webp",
            uploaded_by = user.id,
            commit = False,
        )
        db_session.add(attachment)
        db_session.commit()

        assert (
            f"<TicketAttachment {attachment.id} for Ticket {ticket.id}>"
            == repr(attachment)
        )

    def test_create_attachment(self, db_session, ticket, user):
        """
        Test creating an attachment with the create method
        """
        attachment = TicketAttachment.create_attachment(
            ticket_id = ticket.id,
            s3_key = "support-tickets/1/abc123.webp",
            bucket_name = "my-bucket",
            filename = "screenshot.webp",
            file_size = 2048,
            content_type = "image/webp",
            uploaded_by = user.id,
        )

        refreshed_attachment = TicketAttachment.find_by_id(attachment.id)
        assert refreshed_attachment is not None
        assert refreshed_attachment.ticket_id == ticket.id
        assert refreshed_attachment.file_upload.s3_key == "support-tickets/1/abc123.webp"
        assert refreshed_attachment.file_upload.bucket_name == "my-bucket"
        assert refreshed_attachment.file_upload.filename == "screenshot.webp"
        assert refreshed_attachment.file_upload.file_size == 2048
        assert refreshed_attachment.file_upload.content_type == "image/webp"
        assert refreshed_attachment.file_upload.uploaded_by == user.id
        assert refreshed_attachment.attached_at is not None

    def test_create_attachment_respects_commit_flag(
        self,
        db_session,
        ticket,
        user
    ):
        """
        Test that create respects the commit flag
        """
        with patch.object(db_session, "commit") as mock_commit:
            attachment = TicketAttachment.create_attachment(
                ticket_id = ticket.id,
                s3_key = "support-tickets/1/no-commit.webp",
                bucket_name = "test-bucket",
                filename = "no-commit.webp",
                file_size = 512,
                content_type = "image/webp",
                uploaded_by = user.id,
                commit = False,
            )
            mock_commit.assert_not_called()
            assert attachment.file_upload.filename == "no-commit.webp"

        with patch.object(db_session, "commit") as mock_commit:
            attachment = TicketAttachment.create_attachment(
                ticket_id = ticket.id,
                s3_key = "support-tickets/1/with-commit.webp",
                bucket_name = "test-bucket",
                filename = "with-commit.webp",
                file_size = 512,
                content_type = "image/webp",
                uploaded_by = user.id,
                commit = True,
            )
            mock_commit.assert_called_once()

    def test_create_attachment_validates_file_size(
        self,
        db_session,
        ticket,
        user
    ):
        """
        Test that attachment creation validates file size
        """
        with pytest.raises(ValidationError) as exc_info:
            TicketAttachment.create_attachment(
                ticket_id = ticket.id,
                s3_key = "support-tickets/1/huge.webp",
                bucket_name = "test-bucket",
                filename = "huge.webp",
                file_size = config.TICKET_ATTACHMENT_MAX_SIZE + 1,
                content_type = "image/webp",
                uploaded_by = user.id,
            )
        assert "File size" in str(exc_info.value)

    def test_create_attachment_validates_ticket_exists(
        self,
        db_session,
        user
    ):
        """
        Test that attachment creation validates ticket exists
        """
        with pytest.raises(ValidationError) as exc_info:
            TicketAttachment.create_attachment(
                ticket_id = 999999,  # Non existent ticket
                s3_key = "support-tickets/999999/test.webp",
                bucket_name = "test-bucket",
                filename = "test.webp",
                file_size = 1024,
                content_type = "image/webp",
                uploaded_by = user.id,
            )
        assert "Ticket" in str(exc_info.value) or "ticket_id" in str(
            exc_info.value
        ).lower()

    def test_create_attachment_validates_user_exists(
        self,
        db_session,
        ticket
    ):
        """
        Test that attachment creation validates uploader exists
        """
        with pytest.raises(ValidationError) as exc_info:
            TicketAttachment.create_attachment(
                ticket_id = ticket.id,
                s3_key = "support-tickets/1/test.webp",
                bucket_name = "test-bucket",
                filename = "test.webp",
                file_size = 1024,
                content_type = "image/webp",
                uploaded_by = 999999,  # Non existent user
            )
        assert "User" in str(exc_info.value) or "uploaded_by" in str(
            exc_info.value
        ).lower()

    def test_find_by_ticket(self, db_session, ticket, user):
        """
        Test finding attachments by ticket
        """
        attachment1 = TicketAttachment.create_attachment(
            ticket_id = ticket.id,
            s3_key = "support-tickets/1/first.webp",
            bucket_name = "test-bucket",
            filename = "first.webp",
            file_size = 1024,
            content_type = "image/webp",
            uploaded_by = user.id,
            commit = False,
        )

        attachment2 = TicketAttachment.create_attachment(
            ticket_id = ticket.id,
            s3_key = "support-tickets/1/second.webp",
            bucket_name = "test-bucket",
            filename = "second.webp",
            file_size = 2048,
            content_type = "image/webp",
            uploaded_by = user.id,
            commit = False,
        )

        db_session.add_all([attachment1, attachment2])
        db_session.commit()

        attachments = TicketAttachment.find_by_ticket(ticket.id)

        assert len(attachments) == 2
        assert attachments[0].attached_at <= attachments[1].attached_at

    def test_find_by_ticket_empty(self, db_session, ticket):
        """
        Test finding attachments for ticket with no attachments
        """
        attachments = TicketAttachment.find_by_ticket(ticket.id)
        assert len(attachments) == 0

    def test_serialize_attachment(
        self,
        db_session,
        ticket,
        user
    ):
        """
        Test serialization of attachment with proxy URL
        """
        attachment = TicketAttachment.create_attachment(
            ticket_id = ticket.id,
            s3_key = "support-tickets/1/test.webp",
            bucket_name = "test-bucket",
            filename = "test.webp",
            file_size = 1024,
            content_type = "image/webp",
            uploaded_by = user.id,
        )

        data = attachment.serialize()

        assert data["id"] == attachment.id
        assert data["ticket_id"] == ticket.id
        assert data["file_upload_id"] == attachment.file_upload_id
        assert data["filename"] == "test.webp"
        assert data["file_size"] == 1024
        assert data["content_type"] == "image/webp"
        assert data["uploaded_by"] == user.id
        assert data["uploaded_at"] is not None
        assert data["download_url"] == f"/ng/support/me/attachments/{attachment.id}"

    def test_serialize_attachment_admin(
        self,
        db_session,
        ticket,
        user
    ):
        """
        Test serialization of attachment with admin proxy URL
        """
        attachment = TicketAttachment.create_attachment(
            ticket_id = ticket.id,
            s3_key = "support-tickets/1/admin-test.webp",
            bucket_name = "test-bucket",
            filename = "admin-test.webp",
            file_size = 2048,
            content_type = "image/webp",
            uploaded_by = user.id,
        )

        data = attachment.serialize(include_admin_fields=True)

        assert data["id"] == attachment.id
        assert data["ticket_id"] == ticket.id
        assert data["file_upload_id"] == attachment.file_upload_id
        assert data["filename"] == "admin-test.webp"
        assert data["file_size"] == 2048
        assert data["content_type"] == "image/webp"
        assert data["uploaded_by"] == user.id
        assert data["uploaded_at"] is not None
        assert data["download_url"] == f"/ng/admin/support/attachments/{attachment.id}"


    def test_validation_requires_all_fields(self, db_session):
        """
        Test that validation requires all necessary fields
        """
        with pytest.raises(ValidationError):
            TicketAttachment.validate({})

    def test_validation_empty_strings(self, db_session, ticket, user):
        """
        Test that validation rejects empty strings
        """
        with pytest.raises(ValidationError):
            TicketAttachment.validate(
                {
                    "ticket_id": ticket.id,
                    "s3_key": "",
                    "bucket_name": "test-bucket",
                    "filename": "test.webp",
                    "file_size": 1024,
                    "content_type": "image/webp",
                    "uploaded_by": user.id,
                }
            )

    def test_validation_negative_file_size(
        self,
        db_session,
        ticket,
        user
    ):
        """
        Test that validation rejects negative file sizes
        """
        with pytest.raises(ValidationError):
            TicketAttachment.validate(
                {
                    "ticket_id": ticket.id,
                    "s3_key": "support-tickets/1/test.webp",
                    "bucket_name": "test-bucket",
                    "filename": "test.webp",
                    "file_size": -1,
                    "content_type": "image/webp",
                    "uploaded_by": user.id,
                }
            )
