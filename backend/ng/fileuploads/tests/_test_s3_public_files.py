#!/usr/bin/env python3
"""
Standalone test runner for public files S3 functionality
"""

import sys
import os
import io
from unittest.mock import Mock, patch
from werkzeug.datastructures import FileStorage

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
ng_dir = os.path.join(current_dir, '..', '..')  # backend/ng
backend_dir = os.path.join(ng_dir, '..')        # backend
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, '..', 'external', 'CTFd'))

def test_allowed_folders_configuration():
    """Test that allowed folders are properly configured"""
    # Import directly without going through ng module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "public_files",
        os.path.join(os.path.dirname(__file__), "..", "controllers", "public_files.py")
    )
    public_files = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(public_files)
    ALLOWED_FOLDERS = public_files.ALLOWED_FOLDERS

    expected_folders = ['sponsor-logos', 'event-cards', 'favicons']
    assert set(ALLOWED_FOLDERS.keys()) == set(expected_folders), f"Expected {expected_folders}, got {list(ALLOWED_FOLDERS.keys())}"

    # Test sponsor-logos content types
    sponsor_types = ALLOWED_FOLDERS['sponsor-logos']
    assert 'image/png' in sponsor_types
    assert 'image/jpeg' in sponsor_types
    assert 'image/webp' in sponsor_types
    assert 'image/svg+xml' in sponsor_types

    print("✓ ALLOWED_FOLDERS configuration test passed")

def test_file_extension_mapping():
    """Test file extension mapping from content types"""
    from ng.fileuploads.controllers.public_files import get_file_extension

    assert get_file_extension('image/png') == 'png'
    assert get_file_extension('image/jpeg') == 'jpg'
    assert get_file_extension('image/jpg') == 'jpg'
    assert get_file_extension('image/webp') == 'webp'
    assert get_file_extension('image/svg+xml') == 'svg'
    assert get_file_extension('image/x-icon') == 'ico'
    assert get_file_extension('unknown/type') == 'bin'

    print("✓ File extension mapping test passed")

def test_generate_upload_url_invalid_folder():
    """Test generating presigned URL with invalid folder"""
    from ng.fileuploads.controllers.public_files import generate_upload_url

    args = {
        'folder': 'invalid-folder',
        'content_type': 'image/png'
    }

    result, status_code = generate_upload_url(args)

    assert status_code == 400
    assert 'error' in result
    assert 'Invalid folder' in result['error']

    print("✓ Invalid folder validation test passed")

def test_generate_upload_url_invalid_content_type():
    """Test generating presigned URL with invalid content type"""
    from ng.fileuploads.controllers.public_files import generate_upload_url

    args = {
        'folder': 'sponsor-logos',
        'content_type': 'text/plain'
    }

    result, status_code = generate_upload_url(args)

    assert status_code == 400
    assert 'error' in result
    assert 'Invalid content type' in result['error']

    print("✓ Invalid content type validation test passed")

def test_generate_upload_url_valid():
    """Test generating presigned URL with valid parameters"""
    from ng.fileuploads.controllers.public_files import generate_upload_url

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

    print("✓ Valid presigned URL generation test passed")

def test_direct_upload_file_no_file():
    """Test direct upload without providing file"""
    from ng.fileuploads.controllers.public_files import direct_upload_file

    args = {
        'folder': 'sponsor-logos',
        'file': None
    }

    result, status_code = direct_upload_file(args)

    assert status_code == 400
    assert 'error' in result
    assert 'Valid file is required' in result['error']

    print("✓ No file validation test passed")

def test_direct_upload_file_invalid_folder():
    """Test direct upload with invalid folder"""
    from ng.fileuploads.controllers.public_files import direct_upload_file

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

    print("✓ Invalid folder in direct upload test passed")

@patch('ng.fileuploads.controllers.public_files.requests.put')
def test_direct_upload_file_success(mock_requests_put):
    """Test successful direct file upload to S3"""
    from ng.fileuploads.controllers.public_files import direct_upload_file

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

    print("✓ Direct upload success test passed")

def run_all_tests():
    """Run all S3 public files tests"""
    print("=== Running S3 Public Files Tests ===")

    try:
        test_allowed_folders_configuration()
        test_file_extension_mapping()
        test_generate_upload_url_invalid_folder()
        test_generate_upload_url_invalid_content_type()
        test_generate_upload_url_valid()
        test_direct_upload_file_no_file()
        test_direct_upload_file_invalid_folder()
        test_direct_upload_file_success()

        print("\n🎉 All S3 public files tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)