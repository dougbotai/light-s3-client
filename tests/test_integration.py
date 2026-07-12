import os
import io
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from light_s3_client import Client
from light_s3_client.exceptions import S3Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use default credentials if environment variables are not set
S3_SERVER = os.getenv("s3_server", "http://localhost:5000")
S3_ACCESS_KEY = os.getenv("s3_access_key", "minioadmin")
S3_SECRET_KEY = os.getenv("s3_secret_key", "minioadmin")
S3_BUCKET = os.getenv("s3_bucket", "test-bucket")
S3_REGION = os.getenv("s3_region", "us-east-1")


@pytest.fixture(scope="module")
def s3_client():
    return Client(
        access_key=S3_ACCESS_KEY,
        secret_key=S3_SECRET_KEY,
        region=S3_REGION,
        server=S3_SERVER,
    )


@pytest.fixture(scope="module")
def test_key():
    return "integration_test_file.txt"


@pytest.fixture(scope="module")
def test_content():
    return b"Integration test content."


@pytest.fixture(scope="module")
def mock_response():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = "<TestResponse></TestResponse>"
    mock_resp.content = b"<TestResponse></TestResponse>"
    return mock_resp


@pytest.fixture(scope="module", autouse=True)
def ensure_minio_available(s3_client):
    """
    Ensure MinIO is reachable and the test bucket exists before any
    integration tests in this module run.
    """
    import requests

    try:
        resp = requests.get(f"{S3_SERVER}/minio/health/live", timeout=5)
        assert resp.status_code == 200, f"MinIO health check failed: {resp.status_code}"
    except requests.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to MinIO at {S3_SERVER}. "
            "Start it with: docker-compose up -d"
        )

    # Ensure the bucket exists
    try:
        s3_client.create_bucket(S3_BUCKET)
    except Exception:
        # Bucket may already exist — that's fine
        pass

@pytest.mark.integration
def test_client_initialization():
    """Test that Client can be initialized properly"""
    client = Client(
        access_key="test_access_key",
        secret_key="test_secret_key",
        region="us-east-1"
    )
    assert client.access_key == "test_access_key"
    assert client.secret_key == "test_secret_key"
    assert client.region == "us-east-1"

@pytest.mark.integration
def test_upload_fileobj(s3_client, test_key, test_content):
    """Test upload_fileobj with real S3 connection"""
    fileobj = io.BytesIO(test_content)
    response = s3_client.upload_fileobj(fileobj, S3_BUCKET, test_key)
    print(f"Uploaded file to bucket: {S3_BUCKET}, key: {test_key}, status: {getattr(response, 'status_code', None)}")
    assert response is not None
    assert response.status_code in (200, 201)


@pytest.mark.integration
def test_list_objects(s3_client, test_key):
    """Test list_objects with real S3 connection"""
    objects = s3_client.list_objects(S3_BUCKET, Prefix="integration_test")
    print(f"Listing files in bucket: {S3_BUCKET} with prefix 'integration_test': {len(objects)} keys found")
    assert isinstance(objects, list)
    assert any(test_key in obj for obj in objects)


@pytest.mark.integration
def test_get_object(s3_client, test_key):
    """Test get_object with real S3 connection"""
    exists = s3_client.get_object(S3_BUCKET, test_key)
    print(f"Checked existence of key: {test_key} in bucket: {S3_BUCKET} - Exists: {exists}")
    assert exists is True


@pytest.mark.integration
def test_download_file(s3_client, test_key, test_content):
    """Test download_file with real S3 connection"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
    try:
        s3_client.download_file(S3_BUCKET, test_key, filename)
        with open(filename, "rb") as f:
            data = f.read()
        print(f"Downloaded file from bucket: {S3_BUCKET}, key: {test_key}, bytes: {len(data)}")
        assert data == test_content
    finally:
        os.remove(filename)


@pytest.mark.integration
def test_delete_file(s3_client, test_key):
    """Test delete_file with real S3 connection"""
    s3_client.delete_file(S3_BUCKET, test_key)
    print(f"Deleted key: {test_key} from bucket: {S3_BUCKET}")
    exists = s3_client.get_object(S3_BUCKET, test_key)
    print(f"Checked existence after delete for key: {test_key} in bucket: {S3_BUCKET} - Exists: {exists}")
    assert exists is False

@pytest.mark.integration
def test_unit_signature_creation():
    """Test signature creation logic directly"""
    # This would test the core authentication logic
    pass

@pytest.mark.integration
def test_unit_authentication_flow():
    """Test authentication flow"""
    # This would test the authentication flow logic
    pass

@pytest.mark.integration
def test_error_handling_scenarios():
    """Test error handling scenarios"""
    # This would test various error conditions
    pass

@pytest.mark.integration
def test_mock_s3_service():
    """Test with mock S3 service"""
    # This would test using a mock S3 service
    pass

@pytest.mark.integration
def test_offline_testing():
    """Test offline capabilities"""
    # This would test offline testing without real S3 connection
    pass

@pytest.mark.integration
def test_multipart_upload():
    """Test multipart upload functionality"""
    # This would test multipart upload logic
    pass

@pytest.mark.integration
def test_head_object():
    """Test head_object functionality"""
    # This would test head_object functionality
    pass

@pytest.mark.integration
def test_put_object_tagging():
    """Test put_object_tagging functionality"""
    # This would test tagging functionality
    pass

@pytest.mark.integration
def test_get_object_tagging():
    """Test get_object_tagging functionality"""
    # This would test getting object tags
    pass