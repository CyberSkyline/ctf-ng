"""
Tests for public files API endpoints (S3 direct upload functionality)
"""

import io
import json
import uuid
import pytest
from unittest.mock import Mock, patch, MagicMock
from werkzeug.datastructures import FileStorage

from ..controllers.public_files import (
    generate_upload_url,
    get_public_file,
    list_public_files,
    direct_upload_file,
    get_file_extension,
    ALLOWED_FOLDERS
)


class TestPublicFilesAPI:
    """
    Tests for public files S3 integration
    """

    def test_generate_upload_url_valid_sponsor_logo(self):
        """
        Test generating presigned URL for sponsor logo upload
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.generate_upload_url.return_value = {
                'presigned_url': 'https://s3.amazonaws.com/test-bucket/sponsor-logos/test-uuid.png?signature=xyz',
            }
            mock_get_service.return_value = mock_s3_service

            args = {
                'folder': 'sponsor-logos',
                'content_type': 'image/png'
            }
            
            result = generate_upload_url(args)
            
            assert 'presigned_url' in result
            assert 'filename' in result
            assert 'object_key' in result
            assert result['content_type'] == 'image/png'
            assert result['upload_method'] == 'PUT'
            assert result['object_key'].startswith('sponsor-logos/')
            assert result['object_key'].endswith('.png')

    def test_generate_upload_url_invalid_folder(self):
        """
        Test generating presigned URL with invalid folder
        """
        args = {
            'folder': 'invalid-folder',
            'content_type': 'image/png'
        }
        
        result, status_code = generate_upload_url(args)
        
        assert status_code == 400
        assert 'error' in result
        assert 'Invalid folder' in result['error']

    def test_generate_upload_url_invalid_content_type(self):
        """
        Test generating presigned URL with invalid content type for folder
        """
        args = {
            'folder': 'sponsor-logos',
            'content_type': 'text/plain'
        }
        
        result, status_code = generate_upload_url(args)
        
        assert status_code == 400
        assert 'error' in result
        assert 'Invalid content type' in result['error']

    def test_generate_upload_url_s3_not_configured(self):
        """
        Test generating presigned URL when S3 is not configured
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = False
            mock_get_service.return_value = mock_s3_service

            args = {
                'folder': 'sponsor-logos',
                'content_type': 'image/png'
            }
            
            result, status_code = generate_upload_url(args)
            
            assert status_code == 503
            assert 'error' in result
            assert 'File storage not configured' in result['error']

    def test_get_public_file_valid(self):
        """
        Test getting presigned download URL for existing file
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.object_exists.return_value = True
            mock_s3_service.generate_download_url.return_value = 'https://s3.amazonaws.com/test-bucket/sponsor-logos/test.png?signature=xyz'
            mock_get_service.return_value = mock_s3_service

            args = {
                'folder': 'sponsor-logos',
                'filename': 'test.png'
            }
            
            result = get_public_file(args)
            
            assert 'url' in result
            assert result['filename'] == 'test.png'
            assert result['folder'] == 'sponsor-logos'
            assert result['object_key'] == 'sponsor-logos/test.png'

    def test_get_public_file_not_found(self):
        """
        Test getting presigned download URL for non-existent file
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.object_exists.return_value = False
            mock_get_service.return_value = mock_s3_service

            args = {
                'folder': 'sponsor-logos',
                'filename': 'nonexistent.png'
            }
            
            result, status_code = get_public_file(args)
            
            assert status_code == 404
            assert 'error' in result
            assert 'File not found' in result['error']

    def test_get_file_extension_mapping(self):
        """
        Test file extension mapping from content types
        """
        assert get_file_extension('image/png') == 'png'
        assert get_file_extension('image/jpeg') == 'jpg'
        assert get_file_extension('image/jpg') == 'jpg'
        assert get_file_extension('image/webp') == 'webp'
        assert get_file_extension('image/svg+xml') == 'svg'
        assert get_file_extension('image/x-icon') == 'ico'
        assert get_file_extension('unknown/type') == 'bin'

    @patch('ng.fileuploads.controllers.public_files.requests.put')
    def test_direct_upload_file_success(self, mock_requests_put):
        """
        Test successful direct file upload to S3
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            # Mock S3 service
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.generate_upload_url.return_value = {
                'presigned_url': 'https://s3.amazonaws.com/test-bucket/sponsor-logos/12345.png?signature=xyz',
            }
            mock_get_service.return_value = mock_s3_service

            # Mock successful HTTP PUT response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_requests_put.return_value = mock_response

            # Create mock file
            png_data = b'\x89PNG\r\n\x1a\n'  # PNG header
            file_obj = FileStorage(
                stream=io.BytesIO(png_data),
                filename='test.png',
                content_type='image/png'
            )

            args = {
                'folder': 'sponsor-logos',
                'file': file_obj
            }
            
            result = direct_upload_file(args)
            
            assert result['success'] is True
            assert 'file_info' in result
            file_info = result['file_info']
            assert file_info['folder'] == 'sponsor-logos'
            assert file_info['content_type'] == 'image/png'
            assert file_info['original_filename'] == 'test.png'
            assert file_info['file_size'] == len(png_data)
            assert file_info['object_key'].startswith('sponsor-logos/')
            assert file_info['object_key'].endswith('.png')

            # Verify requests.put was called correctly
            mock_requests_put.assert_called_once()
            call_args = mock_requests_put.call_args
            assert call_args[1]['data'] == png_data
            assert call_args[1]['headers']['Content-Type'] == 'image/png'
            assert call_args[1]['timeout'] == 60

    def test_direct_upload_file_invalid_folder(self):
        """
        Test direct upload with invalid folder
        """
        file_obj = FileStorage(
            stream=io.BytesIO(b'test'),
            filename='test.png',
            content_type='image/png'
        )

        args = {
            'folder': 'invalid-folder',
            'file': file_obj
        }
        
        result, status_code = direct_upload_file(args)
        
        assert status_code == 400
        assert 'error' in result
        assert 'Invalid folder' in result['error']

    def test_direct_upload_file_no_file(self):
        """
        Test direct upload without providing file
        """
        args = {
            'folder': 'sponsor-logos',
            'file': None
        }
        
        result, status_code = direct_upload_file(args)
        
        assert status_code == 400
        assert 'error' in result
        assert 'Valid file is required' in result['error']

    def test_direct_upload_file_invalid_content_type(self):
        """
        Test direct upload with invalid content type for folder
        """
        file_obj = FileStorage(
            stream=io.BytesIO(b'test'),
            filename='test.txt',
            content_type='text/plain'
        )

        args = {
            'folder': 'sponsor-logos',
            'file': file_obj
        }
        
        result, status_code = direct_upload_file(args)
        
        assert status_code == 400
        assert 'error' in result
        assert 'Invalid content type' in result['error']

    @patch('ng.fileuploads.controllers.public_files.requests.put')
    def test_direct_upload_file_s3_upload_failure(self, mock_requests_put):
        """
        Test direct upload when S3 upload fails
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            # Mock S3 service
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.generate_upload_url.return_value = {
                'presigned_url': 'https://s3.amazonaws.com/test-bucket/sponsor-logos/12345.png?signature=xyz',
            }
            mock_get_service.return_value = mock_s3_service

            # Mock failed HTTP PUT response
            mock_response = Mock()
            mock_response.status_code = 403  # Forbidden
            mock_requests_put.return_value = mock_response

            # Create mock file
            png_data = b'\x89PNG\r\n\x1a\n'
            file_obj = FileStorage(
                stream=io.BytesIO(png_data),
                filename='test.png',
                content_type='image/png'
            )

            args = {
                'folder': 'sponsor-logos',
                'file': file_obj
            }
            
            result, status_code = direct_upload_file(args)
            
            assert status_code == 500
            assert 'error' in result
            assert 'Failed to upload file to S3' in result['error']

    def test_list_public_files_valid_folder(self):
        """
        Test listing files in a valid folder
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.list_objects.return_value = [
                {
                    'key': 'sponsor-logos/file1.png',
                    'size': 12345,
                    'last_modified': '2024-01-01T00:00:00Z'
                },
                {
                    'key': 'sponsor-logos/file2.jpg',
                    'size': 67890,
                    'last_modified': '2024-01-02T00:00:00Z'
                }
            ]
            mock_get_service.return_value = mock_s3_service

            args = {'folder': 'sponsor-logos'}
            
            result = list_public_files(args)
            
            assert result['folder'] == 'sponsor-logos'
            assert result['count'] == 2
            assert len(result['files']) == 2
            
            file1 = result['files'][0]
            assert file1['filename'] == 'file1.png'
            assert file1['folder'] == 'sponsor-logos'
            assert file1['size'] == 12345
            
            file2 = result['files'][1]
            assert file2['filename'] == 'file2.jpg'
            assert file2['folder'] == 'sponsor-logos'
            assert file2['size'] == 67890

    def test_allowed_folders_configuration(self):
        """
        Test that allowed folders are properly configured
        """
        expected_folders = ['sponsor-logos', 'event-cards', 'favicons']
        
        assert set(ALLOWED_FOLDERS.keys()) == set(expected_folders)
        
        # Test sponsor-logos content types
        sponsor_types = ALLOWED_FOLDERS['sponsor-logos']
        assert 'image/png' in sponsor_types
        assert 'image/jpeg' in sponsor_types
        assert 'image/webp' in sponsor_types
        assert 'image/svg+xml' in sponsor_types
        
        # Test event-cards content types
        event_types = ALLOWED_FOLDERS['event-cards']
        assert 'image/png' in event_types
        assert 'image/jpeg' in event_types
        assert 'image/webp' in event_types
        
        # Test favicons content types
        favicon_types = ALLOWED_FOLDERS['favicons']
        assert 'image/x-icon' in favicon_types
        assert 'image/png' in favicon_types
        assert 'image/svg+xml' in favicon_types


class TestPublicFilesRoutesIntegration:
    """
    Integration tests for public files routes
    """
    
    def test_generate_upload_url_route(self, client):
        """
        Test the generate upload URL route
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.generate_upload_url.return_value = {
                'presigned_url': 'https://s3.amazonaws.com/test-bucket/sponsor-logos/test-uuid.png?signature=xyz',
            }
            mock_get_service.return_value = mock_s3_service

            response = client.get('/ng/fileuploads/generate_upload_url', query_string={
                'folder': 'sponsor-logos',
                'content_type': 'image/png'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'presigned_url' in data
            assert 'filename' in data
            assert data['content_type'] == 'image/png'

    @patch('ng.fileuploads.controllers.public_files.requests.put')
    def test_direct_upload_route(self, mock_requests_put, client):
        """
        Test the direct upload route
        """
        with patch('ng.fileuploads.controllers.public_files.get_s3_service') as mock_get_service:
            # Mock S3 service
            mock_s3_service = Mock()
            mock_s3_service.is_configured.return_value = True
            mock_s3_service.generate_upload_url.return_value = {
                'presigned_url': 'https://s3.amazonaws.com/test-bucket/sponsor-logos/12345.png?signature=xyz',
            }
            mock_get_service.return_value = mock_s3_service

            # Mock successful HTTP PUT response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_requests_put.return_value = mock_response

            # Create test file data
            png_data = b'\x89PNG\r\n\x1a\n'
            
            response = client.post('/ng/fileuploads/upload/direct', data={
                'folder': 'sponsor-logos',
                'file': (io.BytesIO(png_data), 'test.png', 'image/png')
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'file_info' in data
            assert data['file_info']['folder'] == 'sponsor-logos'