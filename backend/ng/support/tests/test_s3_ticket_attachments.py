"""
Comprehensive tests for support ticket attachment S3 functionality with updated file type support
"""

import io
import pytest
from unittest.mock import Mock, patch, MagicMock
from werkzeug.datastructures import FileStorage

from ... import config
from ..services.s3_upload_service import (
    AWSS3UploadService,
    get_s3_upload_service,
)


class TestTicketAttachmentS3Integration:
    """
    Tests for ticket attachment S3 upload/download functionality with multiple file types
    """

    def test_upload_valid_png_image(self, logged_in_client, ticket):
        """
        Test uploading a valid PNG image (now allowed)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        png_data = b'\x89PNG\r\n\x1a\n'  # PNG header
        file_data = io.BytesIO(png_data)

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_attachment'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/test-uuid.png',
                'bucket_name': 'test-bucket',
                'file_size': len(png_data)
            }

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (file_data, 'test-image.png'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "download_url" in data["data"]
            assert data["data"]["ticket_id"] == ticket.id
            assert data["data"]["filename"] == 'test-image.png'
            assert data["data"]["download_url"].startswith("/ng/support/me/attachments/")

    def test_upload_valid_jpeg_image(self, logged_in_client, ticket):
        """
        Test uploading a valid JPEG image (now allowed)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        jpeg_data = b'\xFF\xD8\xFF\xE0'  # JPEG header
        file_data = io.BytesIO(jpeg_data)

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_attachment'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/test-uuid.jpeg',
                'bucket_name': 'test-bucket',
                'file_size': len(jpeg_data)
            }

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (file_data, 'test-image.jpeg'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "download_url" in data["data"]
            assert data["data"]["ticket_id"] == ticket.id
            assert data["data"]["filename"] == 'test-image.jpeg'

    def test_upload_valid_jpg_image(self, logged_in_client, ticket):
        """
        Test uploading a valid JPG image (now allowed)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        jpg_data = b'\xFF\xD8\xFF\xE0'  # JPEG header (same as JPEG)
        file_data = io.BytesIO(jpg_data)

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_attachment'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/test-uuid.jpg',
                'bucket_name': 'test-bucket',
                'file_size': len(jpg_data)
            }

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (file_data, 'test-image.jpg'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "download_url" in data["data"]
            assert data["data"]["ticket_id"] == ticket.id
            assert data["data"]["filename"] == 'test-image.jpg'

    def test_upload_valid_webp_image(self, logged_in_client, ticket):
        """
        Test uploading a valid WebP image (original supported format)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        webp_data = b'RIFF\x00\x00\x00\x00WEBPVP8 '  # WebP header
        file_data = io.BytesIO(webp_data)

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_attachment'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/test-uuid.webp',
                'bucket_name': 'test-bucket',
                'file_size': len(webp_data)
            }

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (file_data, 'test-image.webp'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "download_url" in data["data"]
            assert data["data"]["ticket_id"] == ticket.id
            assert data["data"]["filename"] == 'test-image.webp'

    def test_upload_invalid_file_type_gif(self, logged_in_client, ticket):
        """
        Test uploading a GIF file (should still fail)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        gif_data = io.BytesIO(b'GIF89a')  # GIF header
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (gif_data, 'test-image.gif'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        error_text = str(data).lower()
        assert "allowed" in error_text or "invalid" in error_text

    def test_upload_invalid_file_type_svg(self, logged_in_client, ticket):
        """
        Test uploading an SVG file (should fail)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        svg_data = io.BytesIO(b'<svg xmlns="http://www.w3.org/2000/svg">')
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (svg_data, 'test-image.svg'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_upload_file_size_validation(self, logged_in_client, ticket):
        """
        Test file size validation (over 5MB should fail)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        # Create file larger than 5MB
        large_png_header = b'\x89PNG\r\n\x1a\n'
        large_data = large_png_header + (b'x' * (6 * 1024 * 1024))  # 6MB
        file_data = io.BytesIO(large_data)

        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (file_data, 'large-image.png'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        error_text = str(data).lower()
        assert "size" in error_text or "5" in str(data)

    def test_download_ticket_attachment_user(self, logged_in_client, ticket_attachment):
        """
        Test downloading ticket attachment as user
        """
        with patch(
            'ng.support.services.s3_upload_service.AWSS3UploadService.download_ticket_attachment'
        ) as mock_download:
            mock_download.return_value = {
                'file_stream': io.BytesIO(b'test file content'),
                'content_type': 'image/png',
                'content_length': 17
            }

            response = logged_in_client.get(
                f"/ng/support/me/attachments/{ticket_attachment.id}"
            )

            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'image/png'
            assert b'test file content' == response.data

    def test_download_nonexistent_attachment(self, logged_in_client):
        """
        Test downloading non-existent attachment
        """
        response = logged_in_client.get(
            "/ng/support/me/attachments/99999"
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "not found" in str(data).lower()

    def test_s3_upload_service_configuration(self):
        """
        Test that S3 upload service correctly maps to support-tickets folder
        """
        with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_get_service.return_value = mock_s3_service

            service = get_s3_upload_service()
            assert service is not None

            # Verify folder prefix from config
            assert config.S3_TICKET_ATTACHMENTS_PREFIX == "support-tickets"

    def test_allowed_file_types_configuration(self):
        """
        Test that config correctly defines allowed file types
        """
        expected_types = ['png', 'jpeg', 'jpg', 'webp']
        assert config.TICKET_ATTACHMENT_ALLOWED_TYPES == expected_types

        # Test max size is 5MB
        assert config.TICKET_ATTACHMENT_MAX_SIZE == 5 * 1024 * 1024

    def test_content_type_validation_in_service(self):
        """
        Test content type validation in S3 upload service
        """
        # Mock file with PNG content type
        png_file = Mock()
        png_file.content_type = 'image/png'
        png_file.filename = 'test.png'
        png_file.stream.read.return_value = b'\x89PNG\r\n\x1a\n'
        png_file.stream.seek = Mock()
        png_file.stream.tell.return_value = 8

        with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.upload_file_to_s3.return_value = 'support-tickets/123/test-uuid.png'
            mock_get_service.return_value = mock_s3_service

            service = AWSS3UploadService()
            result = service.upload_ticket_attachment(123, png_file)

            assert result is not None
            assert 'support-tickets/123/' in result['s3_key']

    def test_s3_key_structure(self):
        """
        Test that S3 keys follow the correct structure: support-tickets/{ticket_id}/{uuid}.{ext}
        """
        ticket_id = 123

        with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.upload_file_to_s3.return_value = f'support-tickets/{ticket_id}/abcd1234.png'
            mock_get_service.return_value = mock_s3_service

            # Mock file
            test_file = Mock()
            test_file.content_type = 'image/png'
            test_file.filename = 'test.png'
            test_file.stream.read.return_value = b'\x89PNG\r\n\x1a\n'
            test_file.stream.seek = Mock()
            test_file.stream.tell.return_value = 8

            service = AWSS3UploadService()
            result = service.upload_ticket_attachment(ticket_id, test_file)

            # Verify key structure
            assert result['s3_key'].startswith(f'support-tickets/{ticket_id}/')
            assert result['s3_key'].endswith('.png')

            # Verify other result fields
            assert 'bucket_name' in result
            assert 'file_size' in result
            assert result['file_size'] == 8


class TestTicketAttachmentAdminAccess:
    """
    Tests for admin access to ticket attachments
    """

    def test_admin_download_any_attachment(self, admin_client, ticket_attachment):
        """
        Test that admin can download any attachment
        """
        with patch(
            'ng.support.services.s3_upload_service.AWSS3UploadService.download_ticket_attachment'
        ) as mock_download:
            mock_download.return_value = {
                'file_stream': io.BytesIO(b'admin access test content'),
                'content_type': 'image/jpeg',
                'content_length': 26
            }

            response = admin_client.get(
                f"/ng/admin/support/attachments/{ticket_attachment.id}"
            )

            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'image/jpeg'
            assert b'admin access test content' == response.data

    def test_regular_user_cannot_access_admin_endpoint(self, logged_in_client, ticket_attachment):
        """
        Test that regular users cannot access admin download endpoint
        """
        response = logged_in_client.get(
            f"/ng/admin/support/attachments/{ticket_attachment.id}"
        )

        # Should either be 403 (forbidden) or 404 (not found) depending on route protection
        assert response.status_code in [403, 404]


class TestS3ServiceIntegration:
    """
    Tests for S3 service integration with ticket attachments
    """

    def test_upload_generates_uuid_filename(self):
        """
        Test that upload generates UUID-based filenames
        """
        with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service, \
             patch('uuid.uuid4') as mock_uuid:

            mock_uuid.return_value.hex = 'test123456789abcdef'
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.upload_file_to_s3.return_value = 'support-tickets/123/test123456789abcdef.png'
            mock_get_service.return_value = mock_s3_service

            # Mock file
            test_file = Mock()
            test_file.content_type = 'image/png'
            test_file.filename = 'original.png'
            test_file.stream.read.return_value = b'\x89PNG\r\n\x1a\n'
            test_file.stream.seek = Mock()
            test_file.stream.tell.return_value = 8

            service = AWSS3UploadService()
            result = service.upload_ticket_attachment(123, test_file)

            # Verify UUID was used in filename
            assert 'test123456789abcdef' in result['s3_key']

    def test_file_size_calculation(self):
        """
        Test that file size is correctly calculated using get_file_size helper
        """
        with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service, \
             patch('ng.support.services.s3_upload_service.get_file_size') as mock_get_size:

            expected_size = 1024
            mock_get_size.return_value = expected_size

            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.upload_file_to_s3.return_value = 'support-tickets/123/test.png'
            mock_get_service.return_value = mock_s3_service

            # Mock file
            test_file = Mock()
            test_file.content_type = 'image/png'
            test_file.filename = 'test.png'
            test_file.stream.read.return_value = b'x' * expected_size
            test_file.stream.seek = Mock()

            service = AWSS3UploadService()
            result = service.upload_ticket_attachment(123, test_file)

            # Verify file size was calculated correctly
            assert result['file_size'] == expected_size
            mock_get_size.assert_called_once_with(test_file)

    def test_error_handling_s3_unavailable(self):
        """
        Test error handling when S3 service is unavailable
        """
        with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service:
            mock_get_service.return_value = None

            service = AWSS3UploadService()

            test_file = Mock()
            result = service.upload_ticket_attachment(123, test_file)

            # Should return None or raise exception when S3 unavailable
            assert result is None