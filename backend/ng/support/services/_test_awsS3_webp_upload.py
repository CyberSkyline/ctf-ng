#!/usr/bin/env python3
"""
Test script for AWS S3 WebP image upload
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


def test_s3_upload():
    """
    Test if S3 upload service is configured and can upload files
    """
    try:
        project_root = setup_project_paths()

        if not load_env_file(project_root):
            print("Cannot proceed without environment configuration")
            return False

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
        print(f"ERROR: Test image not found at {test_image_path}")
        print(
            "Please download a WebP image and name it 'test-upload-img.webp'"
        )
        return False

    app = create_ctfd()

    try:
        with app.app_context():
            config_vars = {
                'AWS_S3_ACCESS_KEY_ID':
                os.getenv('AWS_S3_ACCESS_KEY_ID'),
                'AWS_S3_SECRET_ACCESS_KEY':
                os.getenv('AWS_S3_SECRET_ACCESS_KEY'),
                'AWS_DEFAULT_REGION':
                os.getenv('AWS_DEFAULT_REGION',
                          'us-east-1'),
                'AWS_S3_BUCKET_NAME':
                os.getenv('AWS_S3_BUCKET_NAME'),
            }

            for key, value in config_vars.items():
                app.config[key] = value

            print("AWS S3 CONFIGURATION")
            print(
                f"AWS S3 Access Key: {'SET' if app.config['AWS_S3_ACCESS_KEY_ID'] else 'NOT SET'}"
            )
            print(
                f"AWS S3 Secret Key: {'SET' if app.config['AWS_S3_SECRET_ACCESS_KEY'] else 'NOT SET'}"
            )
            print(
                f"AWS Default Region: {app.config['AWS_DEFAULT_REGION']}"
            )
            print(
                f"AWS S3 Bucket Name: {app.config['AWS_S3_BUCKET_NAME']}"
            )

            s3_service = get_s3_upload_service()
            print(
                f"AWS S3 Configured: {'YES' if s3_service.is_configured() else 'NO'}"
            )

            if not s3_service.is_configured():
                print(
                    "ERROR: AWS S3 not configured - upload test cannot proceed"
                )
                print(
                    "\nMake sure the following environment variables are set in .env.dev:"
                )
                print("  - AWS_S3_ACCESS_KEY_ID")
                print("  - AWS_S3_SECRET_ACCESS_KEY")
                print("  - AWS_S3_BUCKET_NAME")
                return False

            print(f"Reading test image from: {test_image_path}")
            with open(test_image_path, 'rb') as f:
                image_data = f.read()

            file_size_kb = len(image_data) / 1024
            print(f"Image size: {file_size_kb:.2f} KB")

            file_stream = BytesIO(image_data)
            file_storage = FileStorage(
                stream = file_stream,
                filename = 'test-upload-img.webp',
                content_type = 'image/webp'
            )

            test_ticket_id = 99999
            print(
                f"\nAttempting upload to S3 (ticket_id={test_ticket_id})..."
            )

            upload_result = s3_service.upload_ticket_attachment(
                file=file_storage,
                ticket_id=test_ticket_id,
                file_extension='webp'
            )

            if upload_result:
                print("Image uploaded!")
                print(f"S3 Key: {upload_result['s3_key']}")
                print(f"Bucket: {upload_result['bucket_name']}")
                print(f"File Size: {upload_result['file_size']} bytes")

                return True
            else:
                print("FAILED: Could not upload image to S3")
                print("Check the logs above for error details")
                return False

    finally:
        destroy_ctfd(app)


def main():
    """
    Main function
    """
    print("AWS S3 WEBP UPLOAD TEST")

    try:
        success = test_s3_upload()
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
