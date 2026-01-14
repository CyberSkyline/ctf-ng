import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage

from ng.support.controllers.all_actions.upload_attachment import upload_attachment
from ng.support.controllers.all_actions.download_attachment import download_attachment
from ng.core.exceptions import ValidationError


def _png_bytes():
    # Minimal valid 1x1 PNG image data
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde\x00\x00\x00\nIDATx\xdac\xf8\xff\xff?\x00\x05\xfe\x02\xfeA^\xa6\x9b"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.mark.db
class TestUploadAttachment:
    def test_upload_attachment_success(self, request_context, db_session, user, ticket, s3_service):
        file_data = _png_bytes()
        file = FileStorage(
            stream=BytesIO(file_data),
            filename='test-image.png',
            content_type='image/png'
        )

        attachment = upload_attachment(file, ticket, user.id)

        assert attachment is not None
        assert attachment.ticket_id == ticket.id
        assert attachment.file_upload.filename == 'test-image.png'
        assert attachment.file_upload.file_size == len(file_data)

    def test_upload_attachment_no_file(self, request_context, db_session, user, ticket):
        with pytest.raises(ValidationError, match="No file provided"):
            upload_attachment(None, ticket, user.id)

    def test_upload_attachment_closed_ticket(self, request_context, db_session, user, ticket):
        ticket.close_ticket(commit=True)

        file = FileStorage(
            stream=BytesIO(b'data'),
            filename='test.png',
            content_type='image/png'
        )

        with pytest.raises(ValidationError, match="Ticket is closed"):
            upload_attachment(file, ticket, user.id)

    def test_upload_attachment_invalid_type(self, request_context, db_session, user, ticket):
        file = FileStorage(
            stream=BytesIO(b'text content'),
            filename='test.txt',
            content_type='text/plain'
        )

        with pytest.raises(ValidationError, match="File must be a valid image"):
            upload_attachment(file, ticket, user.id)

    def test_upload_attachment_file_too_large(self, request_context, db_session, user, ticket):
        from ng import config
        large_data = b'x' * (config.TICKET_ATTACHMENT_MAX_SIZE + 1)
        file = FileStorage(
            stream=BytesIO(large_data),
            filename='large.png',
            content_type='image/png'
        )

        with pytest.raises(ValidationError, match="File must be smaller"):
            upload_attachment(file, ticket, user.id)


@pytest.mark.db
class TestDownloadAttachment:
    def test_download_attachment_redirect(self, request_context, db_session, user, ticket, s3_service, s3_client, s3_bucket):
        from ng.support.models import TicketAttachment
        from ng.core.models.FileUpload import FileUpload

        s3_client.put_object(Bucket=s3_bucket, Key='support-tickets/1/test.png', Body=b'data')

        FileUpload.create_file_upload(
            s3_key='support-tickets/1/test.png',
            bucket_name=s3_bucket,
            filename='test.png',
            file_size=100,
            content_type='image/png',
            uploaded_by=user.id
        )

        attachment = TicketAttachment.create_attachment(
            ticket_id=ticket.id,
            s3_key='support-tickets/1/test.png',
            bucket_name=s3_bucket,
            filename='test.png',
            file_size=100,
            content_type='image/png',
            uploaded_by=user.id
        )

        db_session.commit()

        response = download_attachment(attachment)

        assert response.status_code == 302
        assert 'Location' in response.headers
        assert s3_bucket in response.headers['Location']
