#!/usr/bin/env python3
"""
Test script for MinIO WebP image upload
"""

import os
import sys
import traceback
from pathlib import Path
from io import BytesIO


def setup_project_paths():
    """
    Set up project paths
    """
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent.parent.parent

    ctfd_path = project_root / "external" / "CTFd"
    backend_path = project_root / "backend"

    if not ctfd_path.exists():
        raise FileNotFoundError(f"CTFd not found at {ctfd_path}")

    if not backend_path.exists():
        raise FileNotFoundError(f"Backend not found at {backend_path}")

    sys.path.insert(0, str(ctfd_path))
    sys.path.insert(0, str(backend_path))
    return project_root


def load_env_file(project_root):
    """
    Load environment variables from .env file
    """
    env_file = project_root / ".env.dev"

    if not env_file.exists():
        print(f"Environment file not found: {env_file}")
        return False

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    print(f"Loaded environment from {env_file}")
    return True


def test_minio_upload():
    """
    Test if MinIO upload service is configured and can upload files
    """
    try:
        project_root = setup_project_paths()

        if not load_env_file(project_root):
            print("Cannot proceed without environment configuration")
            return False

        os.environ['USE_MINIO'] = 'true'

        from ng.core.tests.helpers import create_ctfd, destroy_ctfd
        from ng.support.services.s3_upload_service import get_s3_upload_service
        from werkzeug.datastructures import FileStorage

    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"Path error: {e}")
        return False

    test_image_path = Path(__file__).parent / "test-upload-img.webp"
    if not test_image_path.exists():
        print(f"WARNING: Test image not found at {test_image_path}")
        print("Creating a minimal WebP test file...")
        webp_header = b'RIFF\x1a\x00\x00\x00WEBPVP8 \x0e\x00\x00\x000\x01\x00\x9d\x01\x2a\x01\x00\x01\x00'
        with open(test_image_path, 'wb') as f:
            f.write(webp_header)
        print(f"Created minimal test WebP at {test_image_path}")

    app = create_ctfd()

    try:
        with app.app_context():
            config_vars = {
                'USE_MINIO': 'true',
                'MINIO_ACCESS_KEY': os.getenv('MINIO_ACCESS_KEY', 'ctfd-dev'),
                'MINIO_SECRET_KEY': os.getenv('MINIO_SECRET_KEY', 'ctfd-dev-secret-key-12345'),
                'MINIO_ENDPOINT': 'http://localhost:9000',  # Force localhost for host machine
                'MINIO_BUCKET': os.getenv('MINIO_BUCKET', 'ctfd-uploads'),
            }

            aws_config = {
                'AWS_S3_ACCESS_KEY_ID': os.getenv('AWS_S3_ACCESS_KEY_ID'),
                'AWS_S3_SECRET_ACCESS_KEY': os.getenv('AWS_S3_SECRET_ACCESS_KEY'),
                'AWS_DEFAULT_REGION': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                'AWS_S3_BUCKET_NAME': os.getenv('AWS_S3_BUCKET_NAME'),
            }

            for key, value in config_vars.items():
                app.config[key] = value
            for key, value in aws_config.items():
                app.config[key] = value

            print("STORAGE CONFIGURATION")
            print(f"USE_MINIO: {app.config.get('USE_MINIO')}")
            print(f"MinIO Endpoint: {app.config.get('MINIO_ENDPOINT')}")
            print(f"MinIO Bucket: {app.config.get('MINIO_BUCKET')}")
            print(f"MinIO Access Key: {'SET' if app.config.get('MINIO_ACCESS_KEY') else 'NOT SET'}")
            print(f"MinIO Secret Key: {'SET' if app.config.get('MINIO_SECRET_KEY') else 'NOT SET'}")

            s3_service = get_s3_upload_service()

            print(f"\nStorage Type: {s3_service.get_storage_type()}")
            print(f"Storage Configured: {'YES' if s3_service.is_configured() else 'NO'}")

            if not s3_service.is_configured():
                print("\nERROR: Storage not configured - upload test cannot proceed")
                print("\nMake sure:")
                print("1. MinIO is running: docker ps | grep minio")
                print("2. Bucket is created: npm run minio")
                print("3. Environment variables are set in .env.dev:")
                print("   - MINIO_ACCESS_KEY=ctfd-dev")
                print("   - MINIO_SECRET_KEY=ctfd-dev-secret-key-12345")
                print("   - MINIO_ENDPOINT=http://minio:9000 (or http://localhost:9000)")
                print("   - MINIO_BUCKET=ctfd-uploads")
                return False

            if s3_service.get_storage_type() != "minio":
                print(f"\nWARNING: Expected MinIO but got {s3_service.get_storage_type()}")
                print("Continuing anyway...")

            print(f"\nReading test image from: {test_image_path}")
            with open(test_image_path, 'rb') as f:
                image_data = f.read()

            file_size_kb = len(image_data) / 1024
            print(f"Image size: {file_size_kb:.2f} KB")

            file_stream = BytesIO(image_data)
            file_storage = FileStorage(
                stream=file_stream,
                filename='test-minio-upload.webp',
                content_type='image/webp'
            )

            test_ticket_id = 99999
            print(f"\nAttempting upload to {s3_service.get_storage_type()} (ticket_id={test_ticket_id})...")

            upload_result = s3_service.upload_ticket_image(
                file=file_storage,
                ticket_id=test_ticket_id,
                file_extension='webp'
            )

            if upload_result:
                print(f"SUCCESS: Image uploaded to {s3_service.get_storage_type()}!")
                print(f"S3 Key: {upload_result['s3_key']}")
                print(f"Bucket: {upload_result['bucket_name']}")
                print(f"File Size: {upload_result['file_size']} bytes")

                from ng import config
                presigned_url = s3_service.generate_presigned_url(
                    bucket_name=upload_result['bucket_name'],
                    s3_key=upload_result['s3_key'],
                    expiration=config.PRESIGNED_URL_EXPIRATION_SECONDS
                )

                if presigned_url:
                    print(f"\nPresigned URL (valid for 1 hour):\n{presigned_url}")
                    print("\nVerify the upload by:")
                    print("1. Opening the presigned URL in your browser")
                    print("2. Checking MinIO Console: http://localhost:9001")
                    print("   - Login: ctfd-dev / ctfd-dev-secret-key-12345")
                    print(f"   - Browse to: {upload_result['s3_key']}")
                else:
                    print("\nWarning: Could not generate presigned URL")

                return True
            else:
                print("FAILED: Could not upload image")
                print("Check the logs above for error details")
                print("\nTroubleshooting:")
                print("1. Is MinIO running? docker ps | grep minio")
                print("2. Is the bucket created? npm run minio")
                print("3. Check MinIO logs: docker logs ng-minio")
                return False

    finally:
        destroy_ctfd(app)


def main():
    """
    Main function
    """
    print("MINIO S3-COMPATIBLE STORAGE UPLOAD TEST")

    try:
        success = test_minio_upload()

        if success:
            print("TEST COMPLETED SUCCESSFULLY!")
        else:
            print("TEST COMPLETED WITH ISSUES")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
