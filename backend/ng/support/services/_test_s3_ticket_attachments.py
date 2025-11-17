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

def test_configuration():
    """Test S3 ticket attachment configuration"""
    from ng import config
    
    # Test that all expected file types are allowed
    expected_types = ['png', 'jpeg', 'jpg', 'webp']
    assert config.TICKET_ATTACHMENT_ALLOWED_TYPES == expected_types, f"Expected {expected_types}, got {config.TICKET_ATTACHMENT_ALLOWED_TYPES}"
    
    print(f"[PASS] Config - Max size: {config.TICKET_ATTACHMENT_MAX_SIZE / (1024*1024)}MB")
    print(f"[PASS] Config - Allowed types: {config.TICKET_ATTACHMENT_ALLOWED_TYPES}")
    print(f"[PASS] Config - S3 prefix: {config.S3_TICKET_ATTACHMENTS_PREFIX}")

def test_service_import():
    """Test S3 upload service can be imported and instantiated"""
    from ng.support.services.s3_upload_service import SupportS3Service
    
    # Test service instantiation
    service = SupportS3Service()
    assert service is not None
    
    print("[PASS] Service import and instantiation successful")

def test_mock_file_upload():
    """Test mock file upload workflow"""

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
        from ng.support.services.s3_upload_service import SupportS3Service
        service = SupportS3Service()
        with patch('ng.support.services.s3_upload_service.get_file_size', return_value=8):
            result = service.upload_ticket_attachment(test_file, 123)

            assert result is not None
            assert 'support-tickets/123/' in result['s3_key']
            assert result['file_size'] == 8
            
    print("[PASS] Mock file upload workflow successful")

def run_all_tests():
    """Run all S3 ticket attachment tests"""
    print("=== S3 Ticket Attachment Tests ===")
    
    try:
        test_configuration()
        test_service_import()
        test_mock_file_upload()
        
        print("\n[SUCCESS] All S3 ticket attachment tests passed!")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_all_tests()