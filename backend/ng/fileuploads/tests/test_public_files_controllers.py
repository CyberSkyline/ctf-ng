import pytest
from io import BytesIO
from flask import json

from ng.fileuploads.controllers.public_files import generate_unique_filename, generate_upload_url, get_public_file, list_public_files, search_public_files


@pytest.mark.db
class TestGenerateUploadURL:
    def test_generate_upload_url_success(self, request_context, db_session, s3_service):
        result = generate_upload_url({
            'folder': 'sponsor-logos',
            'filename': 'test-logo.png',
            'content_type': 'image/png',
            'allow_overwrite': False
        })

        assert result[1] == 200
        data = result[0]
        assert data['success'] is True
        assert 'upload_url' in data['data']
        assert data['data']['filename'] == 'test-logo.png'
        assert data['data']['folder'] == 'sponsor-logos'
        assert data['data']['upload_method'] == 'PUT'

    def test_invalid_folder(self, request_context, db_session, s3_service):
        result = generate_upload_url({
            'folder': 'invalid-folder',
            'filename': 'test.png',
            'content_type': 'image/png'
        })

        data = result[0]
        assert data['success'] is False
        assert result[1] == 400

    def test_invalid_content_type(self, request_context, db_session, s3_service):
        result = generate_upload_url({
            'folder': 'sponsor-logos',
            'filename': 'test.txt',
            'content_type': 'text/plain'
        })

        data = result[0]
        assert data['success'] is False
        assert result[1] == 400

    def test_missing_filename(self, request_context, db_session, s3_service):
        result = generate_upload_url({
            'folder': 'sponsor-logos',
            'content_type': 'image/png'
        })

        data = result[0]
        assert data['success'] is False
        assert result[1] == 400

    def test_with_include_urls(self, request_context, db_session, s3_service):
        result = generate_upload_url({
            'folder': 'event-cards',
            'filename': 'card.webp',
            'content_type': 'image/webp',
            'include_urls': True
        })

        data = result[0]
        assert data['success'] is True
        assert 'download_url' in data['data']


@pytest.mark.db
class TestUniqueFilenameGeneration:
    def test_filename_remains_same_when_no_conflict(self, db_session, s3_service):
        filename = generate_unique_filename(s3_service, 'sponsor-logos', 'new-logo.png')
        assert filename == 'new-logo.png'

    def test_filename_appends_number_on_conflict(self, db_session, s3_service, s3_client, s3_bucket):
        s3_client.put_object(Bucket=s3_bucket, Key='sponsor-logos/logo.png', Body=b'test')

        filename = generate_unique_filename(s3_service, 'sponsor-logos', 'logo.png')
        assert filename == 'logo_1.png'

    def test_filename_increments_until_unique(self, db_session, s3_service, s3_client, s3_bucket):
        s3_client.put_object(Bucket=s3_bucket, Key='sponsor-logos/logo.png', Body=b'test')
        s3_client.put_object(Bucket=s3_bucket, Key='sponsor-logos/logo_1.png', Body=b'test')
        s3_client.put_object(Bucket=s3_bucket, Key='sponsor-logos/logo_2.png', Body=b'test')

        filename = generate_unique_filename(s3_service, 'sponsor-logos', 'logo.png')
        assert filename == 'logo_3.png'

    def test_allow_overwrite_returns_original_filename(self, db_session, s3_service, s3_client, s3_bucket):
        s3_client.put_object(Bucket=s3_bucket, Key='sponsor-logos/logo.png', Body=b'test')

        filename = generate_unique_filename(s3_service, 'sponsor-logos', 'logo.png', allow_overwrite=True)
        assert filename == 'logo.png'

    def test_filename_preserves_extension(self, db_session, s3_service, s3_client, s3_bucket):
        s3_client.put_object(Bucket=s3_bucket, Key='favicons/icon.ico', Body=b'test')

        filename = generate_unique_filename(s3_service, 'favicons', 'icon.ico')
        assert filename == 'icon_1.ico'


@pytest.mark.db
class TestGetPublicFile:
    def test_get_existing_file(self, request_context, db_session, s3_service, s3_with_files):
        result = get_public_file({
            'folder': 'sponsor-logos',
            'filename': 'company1.png'
        })

        data = result[0]
        assert data['success'] is True
        assert 'download_url' in data['data']
        assert data['data']['filename'] == 'company1.png'
        assert data['data']['folder'] == 'sponsor-logos'

    def test_get_nonexistent_file(self, request_context, db_session, s3_service):
        result = get_public_file({
            'folder': 'sponsor-logos',
            'filename': 'nonexistent.png'
        })

        data = result[0]
        assert data['success'] is False
        assert result[1] == 404

    def test_missing_parameters(self, request_context, db_session, s3_service):
        result = get_public_file({'folder': 'sponsor-logos'})

        data = result[0]
        assert data['success'] is False
        assert result[1] == 400


@pytest.mark.db
class TestListPublicFiles:
    def test_list_files_in_folder(self, request_context, db_session, s3_service, s3_with_files):
        result = list_public_files({'folder': 'sponsor-logos'})

        data = result[0]
        assert data['success'] is True
        assert len(data['data']['files']) == 2
        filenames = [f['filename'] for f in data['data']['files']]
        assert 'company1.png' in filenames
        assert 'company2.jpg' in filenames

    def test_list_with_download_urls(self, request_context, db_session, s3_service, s3_with_files):
        result = list_public_files({
            'folder': 'sponsor-logos',
            'include_urls': True
        })

        data = result[0]
        assert data['success'] is True
        for file_info in data['data']['files']:
            assert 'download_url' in file_info
            assert file_info['download_url'] is not None

    def test_list_invalid_folder(self, request_context, db_session, s3_service):
        result = list_public_files({'folder': 'invalid-folder'})

        data = result[0]
        assert data['success'] is False
        assert result[1] == 400


@pytest.mark.db
class TestSearchPublicFiles:
    def test_search_by_folder_and_filename(self, request_context, db_session, s3_service, s3_with_files):
        result = search_public_files({
            'folder': 'sponsor-logos',
            'filename': 'company1.png'
        })

        data = result[0]
        assert data['success'] is True
        assert len(data['data']['files']) == 1
        assert data['data']['files'][0]['filename'] == 'company1.png'

    def test_search_nonexistent_file(self, request_context, db_session, s3_service):
        result = search_public_files({
            'folder': 'sponsor-logos',
            'filename': 'nonexistent.png'
        })

        data = result[0]
        assert data['success'] is True
        assert len(data['data']['files']) == 0

    def test_search_all_folders(self, request_context, db_session, s3_service, s3_with_files):
        result = search_public_files({'filename': 'company'})

        data = result[0]
        assert data['success'] is True
        assert len(data['data']['files']) >= 2

    def test_search_invalid_folder(self, request_context, db_session, s3_service):
        result = search_public_files({
            'folder': 'invalid-folder',
            'filename': 'test.png'
        })

        data = result[0]
        assert data['success'] is False
        assert result[1] == 400
