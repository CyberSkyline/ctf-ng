#!/usr/bin/env python3
"""
Standalone test for S3 ticket attachment functionality
Bypasses the conftest.py import issues by importing only what's needed
"""

import sys
import os
from unittest.mock import Mock, patch

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
ng_dir = os.path.join(current_dir, '..', '..')  # backend/ng directory
backend_dir = os.path.join(ng_dir, '..')        # backend directory
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, '..', 'external', 'CTFd'))

def test_s3_ticket_attachments():
    """Test S3 ticket attachment functionality"""
    print("=== Testing S3 Ticket Attachment Functionality ===")

    # Test config values
    from ng import config
    print(f"Max attachment size: {config.TICKET_ATTACHMENT_MAX_SIZE / (1024*1024)}MB")
    print(f"Allowed types: {config.TICKET_ATTACHMENT_ALLOWED_TYPES}")
    print(f"S3 prefix: {config.S3_TICKET_ATTACHMENTS_PREFIX}")

    # Test that all expected file types are allowed
    expected_types = ['png', 'jpeg', 'jpg', 'webp']
    assert config.TICKET_ATTACHMENT_ALLOWED_TYPES == expected_types, f"Expected {expected_types}, got {config.TICKET_ATTACHMENT_ALLOWED_TYPES}"

    # Test S3 upload service can be imported
    try:
        from ng.support.services.s3_upload_service import AWSS3UploadService
        print("S3 upload service imports successfully")

        # Test service instantiation
        service = AWSS3UploadService()
        assert service is not None
        print("S3 upload service can be instantiated")

    except Exception as e:
        print(f"S3 service import failed: {e}")
        return False

    # Test mock file upload workflow
    with patch('ng.core.services.s3_service.get_s3_service') as mock_get_service:
        mock_s3_service = Mock()
        mock_s3_service.is_configured.return_value = True
        mock_s3_service.upload_file_to_s3.return_value = 'support-tickets/123/test-uuid.png'
        mock_get_service.return_value = mock_s3_service

        # Mock file
        from werkzeug.datastructures import FileStorage
        test_file = Mock(spec=FileStorage)
        test_file.content_type = 'image/png'
        test_file.filename = 'test.png'
        test_file.stream.read.return_value = b'\x89PNG\r\n\x1a\n'
        test_file.stream.seek = Mock()
        test_file.stream.tell.return_value = 8

        # Test upload
        service = AWSS3UploadService()
        with patch('ng.support.services.s3_upload_service.get_file_size', return_value=8):
            result = service.upload_ticket_attachment(123, test_file)

            assert result is not None
            assert 'support-tickets/123/' in result['s3_key']
            assert result['file_size'] == 8
            print("Mock file upload test passed")

    print("All S3 ticket attachment tests passed")
    return True

if __name__ == "__main__":
    success = test_s3_ticket_attachments()
    sys.exit(0 if success else 1)