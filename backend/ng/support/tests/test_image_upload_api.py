"""
Tests for support ticket image upload API endpoints
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


class TestUserImageUpload:
    """
    Tests for user image upload API endpoints
    """
    def test_upload_valid_webp_image(self, logged_in_client, ticket):
        """
        Test uploading a valid WebP image
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        webp_data = b'RIFF\x00\x00\x00\x00WEBPVP8 '  # WebP header
        file_data = io.BytesIO(webp_data)

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_image'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/test-uuid.webp',
                'bucket_name': 'test-bucket',
                'file_size': len(webp_data)
            }

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (file_data,
                             'test-image.webp'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "image_url" in data["data"]
            assert data["data"]["ticket_id"] == ticket.id
            assert data["data"]["s3_key"] == f'support-tickets/{ticket.id}/test-uuid.webp'

    def test_upload_image_no_file_provided(
        self,
        logged_in_client,
        ticket
    ):
        """
        Test uploading without providing a file
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {'nonce': nonce}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "file" in str(data).lower()

    def test_upload_invalid_file_type_jpg(self, logged_in_client, ticket):
        """
        Test uploading a JPG file (should fail)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        jpg_data = io.BytesIO(b'\xFF\xD8\xFF\xE0')  # JPEG header
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (jpg_data,
                         'test-image.jpg'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "webp" in str(data).lower()

    def test_upload_invalid_file_type_png(self, logged_in_client, ticket):
        """
        Test uploading a PNG file (should fail)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        png_data = io.BytesIO(b'\x89PNG\r\n\x1a\n')  # PNG header
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (png_data,
                         'test-image.png'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_upload_invalid_file_type_gif(self, logged_in_client, ticket):
        """
        Test uploading a GIF file (should fail)
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        gif_data = io.BytesIO(b'GIF89a')  # GIF header
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (gif_data,
                         'test-image.gif'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_upload_file_exceeds_max_size(self, logged_in_client, ticket):
        """
        Test uploading a file that exceeds the maximum size limit
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        large_data = b'x' * (6 * 1024 * 1024)  # 6MB
        file_data = io.BytesIO(large_data)

        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (file_data,
                         'large-image.webp'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "5" in str(data) or "size" in str(data).lower()

    def test_upload_file_exactly_at_max_size(
        self,
        logged_in_client,
        ticket
    ):
        """
        Test uploading a file exactly at the maximum size limit
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        # 5MB
        exact_size_data = b'x' * config.TICKET_IMAGE_MAX_SIZE
        file_data = io.BytesIO(exact_size_data)

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_image'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/exact-size.webp',
                'bucket_name': 'test-bucket',
                'file_size': config.TICKET_IMAGE_MAX_SIZE
            }

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (file_data,
                             'exact-size.webp'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_upload_empty_file(self, logged_in_client, ticket):
        """
        Test uploading an empty file
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        empty_data = io.BytesIO(b'')
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {
                'file': (empty_data,
                         'empty.webp'),
                'nonce': nonce
            }
        )

        # Should be handled gracefully
        assert response.status_code in [400, 500]

    def test_upload_webp_case_insensitive(self, logged_in_client, ticket):
        """
        Test that file extension matching is case insensitive
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_image'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{ticket.id}/test.webp',
                'bucket_name': 'test-bucket',
                'file_size': len(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
            }

            # Uppercase extension
            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (webp_data,
                             'test-image.WEBP'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_upload_to_nonexistent_ticket(self, logged_in_client):
        """
        Test uploading to a ticket that doesn't exist
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
        response = logged_in_client.post(
            "/ng/support/me/tickets/999999/upload_image",
            data = {
                'file': (webp_data,
                         'test.webp'),
                'nonce': nonce
            }
        )

        assert response.status_code == 404

    def test_upload_to_other_users_ticket(
        self,
        logged_in_client,
        other_user_ticket
    ):
        """
        Test that users cannot upload images to other users' tickets
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{other_user_ticket.id}/upload_image",
            data = {
                'file': (webp_data,
                         'test.webp'),
                'nonce': nonce
            }
        )

        assert response.status_code == 403

    def test_upload_s3_failure(self, logged_in_client, ticket):
        """
        Test handling of S3 upload failure
        """
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_image'
        ) as mock_upload:
            # Simulate S3 failure by returning None
            mock_upload.return_value = None

            response = logged_in_client.post(
                f"/ng/support/me/tickets/{ticket.id}/upload_image",
                data = {
                    'file': (webp_data,
                             'test.webp'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "upload" in str(data).lower(
            ) or "fail" in str(data).lower()

    def test_unauthenticated_upload_fails(self, client, ticket):
        """
        Test that unauthenticated users cannot upload images
        """
        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
        response = client.post(
            f"/ng/support/me/tickets/{ticket.id}/upload_image",
            data = {'file': (webp_data,
                             'test.webp')}
        )

        assert response.status_code in [401, 403]

    def test_admin_upload_to_any_ticket(
        self,
        admin_client,
        user,
        ticket_factory
    ):
        """
        Test that admins can upload images to any ticket
        """
        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        other_ticket = ticket_factory(
            subject = "Other user's ticket",
            author_id = user.id
        )

        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')

        with patch(
                'ng.support.services.s3_upload_service.AWSS3UploadService.upload_ticket_image'
        ) as mock_upload:
            mock_upload.return_value = {
                's3_key': f'support-tickets/{other_ticket.id}/admin-upload.webp',
                'bucket_name': 'test-bucket',
                'file_size': len(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
            }

            response = admin_client.post(
                f"/ng/admin/support/tickets/{other_ticket.id}/upload_image",
                data = {
                    'file': (webp_data,
                             'admin-upload.webp'),
                    'nonce': nonce
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "image_url" in data["data"]

    def test_admin_upload_invalid_file_type(self, admin_client, ticket):
        """
        Test that admins also cannot upload non WebP files
        """
        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        jpg_data = io.BytesIO(b'\xFF\xD8\xFF\xE0')
        response = admin_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/upload_image",
            data = {
                'file': (jpg_data,
                         'test.jpg'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400

    def test_admin_upload_exceeds_size_limit(self, admin_client, ticket):
        """
        Test that admins are also subject to file size limits
        """
        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        large_data = b'x' * (6 * 1024 * 1024)  # 6MB
        file_data = io.BytesIO(large_data)

        response = admin_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/upload_image",
            data = {
                'file': (file_data,
                         'large.webp'),
                'nonce': nonce
            }
        )

        assert response.status_code == 400

    def test_non_admin_cannot_access_admin_upload_endpoint(
        self,
        logged_in_client,
        ticket
    ):
        """
        Test that regular users cannot access admin upload endpoint
        """
        webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
        response = logged_in_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/upload_image",
            data = {'file': (webp_data,
                             'test.webp')}
        )

        assert response.status_code in [302, 403]

    @patch('ng.support.services.s3_upload_service.boto3.client')
    def test_s3_service_initialization(self, mock_boto_client, app):
        """
        Test S3 service initializes correctly with valid credentials
        """
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        app.config['AWS_S3_ACCESS_KEY_ID'] = 'test-key'
        app.config['AWS_S3_SECRET_ACCESS_KEY'] = 'test-secret'
        app.config['AWS_DEFAULT_REGION'] = 'us-east-1'

        with app.app_context():
            service = AWSS3UploadService()
            assert service is not None
            assert service.is_configured()

    def test_s3_service_not_configured_without_credentials(self, app):
        """
        Test S3 service handles missing credentials gracefully
        """
        app.config['AWS_S3_ACCESS_KEY_ID'] = None
        app.config['AWS_S3_SECRET_ACCESS_KEY'] = None

        with app.app_context():
            service = AWSS3UploadService()
            assert not service.is_configured()

    @patch('ng.support.services.s3_upload_service.boto3.client')
    def test_s3_upload_generates_unique_filename(
        self,
        mock_boto_client,
        app,
        ticket
    ):
        """
        Test that S3 uploads generate unique filenames using UUIDs
        """
        app.config['AWS_S3_ACCESS_KEY_ID'] = 'test-key'
        app.config['AWS_S3_SECRET_ACCESS_KEY'] = 'test-secret'
        app.config['AWS_S3_BUCKET_NAME'] = 'test-bucket'

        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        with app.app_context():
            service = AWSS3UploadService()

            webp_data = io.BytesIO(b'RIFF\x00\x00\x00\x00WEBPVP8 ')
            file = FileStorage(stream = webp_data, filename = 'test.webp')

            service.upload_ticket_image(
                file=file,
                ticket_id=ticket.id,
                file_extension='webp'
            )

            assert mock_s3_client.upload_fileobj.called
            call_args = mock_s3_client.upload_fileobj.call_args

            s3_key = call_args[0][2]
            assert f"support-tickets/{ticket.id}/" in s3_key
            assert ".webp" in s3_key
