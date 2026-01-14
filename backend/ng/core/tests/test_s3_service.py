import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage
from unittest.mock import patch, MagicMock

from ng.core.services.s3_service import S3Service, get_s3_service, init_s3_service
from ng import config


@pytest.mark.db
class TestS3ServiceConfiguration:
    def test_service_not_configured_without_credentials(self, app, db_session):
        service = S3Service()
        service.init_app(app)
        assert not service.is_configured()

    def test_service_configured_with_mocked_s3(self, db_session, s3_service):
        assert s3_service.is_configured()
        assert s3_service.bucket_name == 'test-ctf-bucket'
        assert s3_service.region_name == 'us-east-1'
        assert s3_service.s3_client is not None

    def test_get_s3_service_singleton(self, db_session, s3_service):
        import ng.core.services.s3_service as s3_module
        s3_module._s3_service_instance = s3_service

        service1 = get_s3_service()
        service2 = get_s3_service()

        assert service1 is service2


@pytest.mark.db
class TestPresignedURLGeneration:
    def test_generate_upload_url_success(self, db_session, s3_service):
        result = s3_service.generate_upload_url(
            folder='sponsor-logos',
            filename='test-logo.png',
            content_type='image/png'
        )

        assert 'presigned_url' in result
        assert 'filename' in result
        assert 'object_key' in result
        assert 'content_type' in result
        assert result['filename'] == 'test-logo.png'
        assert result['object_key'] == 'sponsor-logos/test-logo.png'
        assert result['content_type'] == 'image/png'
        assert 'test-ctf-bucket' in result['presigned_url']

    def test_generate_upload_url_not_configured(self):
        service = S3Service()

        with pytest.raises(Exception, match="S3 service not configured"):
            service.generate_upload_url('test-folder', 'test.txt')

    def test_generate_download_url_success(self, db_session, s3_service, s3_client, s3_bucket):
        object_key = 'test-folder/test-file.txt'
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=object_key,
            Body=b'test content'
        )

        url = s3_service.generate_download_url(object_key, expires_in=600)

        assert url is not None
        assert 'test-ctf-bucket' in url
        assert 'test-folder/test-file.txt' in url

    def test_generate_download_url_not_configured(self):
        service = S3Service()

        with pytest.raises(Exception, match="S3 service not configured"):
            service.generate_download_url('test.txt')

    @patch('ng.core.services.s3_service.RedisCache')
    def test_upload_url_caching(self, mock_redis, db_session, s3_service):
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        s3_service.generate_upload_url(
            folder='test-folder',
            filename='test.txt',
            content_type='text/plain'
        )

        assert mock_redis.set.called


@pytest.mark.db
class TestFileOperations:
    def test_list_objects_with_prefix(self, db_session, s3_service, s3_with_files):
        files = s3_service.list_objects(prefix='sponsor-logos')

        assert len(files) == 2
        assert all('sponsor-logos' in f['key'] for f in files)

    def test_object_exists_true(self, db_session, s3_service, s3_with_files):
        exists = s3_service.object_exists('sponsor-logos/company1.png')
        assert exists is True

    def test_object_exists_false(self, db_session, s3_service, s3_bucket):
        exists = s3_service.object_exists('nonexistent/file.txt')
        assert exists is False

    def test_search_files_by_prefix(self, db_session, s3_service, s3_with_files):
        results = s3_service.search_files(prefix='event-cards', limit=10)

        assert len(results) == 1
        assert results[0]['folder'] == 'event-cards'
        assert results[0]['filename'] == 'event1.webp'


@pytest.mark.db
class TestDirectFileUpload:
    def test_upload_file_direct_success(self, db_session, s3_service, s3_client, s3_bucket):
        file_data = b'test file content'
        file_storage = FileStorage(
            stream=BytesIO(file_data),
            filename='test-upload.txt',
            content_type='text/plain'
        )

        object_key = 'test-uploads/test-upload.txt'
        success = s3_service.upload_file_direct(
            file=file_storage,
            object_key=object_key,
            content_type='text/plain'
        )

        assert success is True

        response = s3_client.get_object(Bucket=s3_bucket, Key=object_key)
        assert response['Body'].read() == file_data


@pytest.mark.db
class TestCacheKeyGeneration:
    def test_generate_cache_key_without_content_type(self, db_session, s3_service):
        key1 = s3_service._generate_cache_key('upload', 'test/file.txt', 3600)
        key2 = s3_service._generate_cache_key('upload', 'test/file.txt', 3600)

        assert key1 == key2
        assert key1.startswith('s3_presigned:')

    def test_get_cache_ttl(self, db_session, s3_service):
        ttl = s3_service._get_cache_ttl(expires_in=3600)
        expected = max(config.URL_CACHE_MIN_TTL, 3600 - config.URL_CACHE_BUFFER_TIME)
        assert ttl == expected
