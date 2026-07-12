# light-s3-client Documentation

## Overview

The `light-s3-client` is a lightweight Python library for interacting with Amazon S3 using the REST API directly, rather than relying on the full Boto3 SDK. This approach reduces dependencies and provides a more focused implementation for specific S3 operations.

## Key Features

- **Lightweight**: Uses only `requests` and `xmltodict` dependencies
- **Direct S3 API**: Implements AWS Signature Version 4 authentication directly
- **Core S3 Operations**: Supports download, upload, delete, and list operations
- **Error Handling**: Provides specific exception types for different error conditions
- **Cross-platform**: Compatible with Python 3.8+

## Development Setup

This project uses `uv` for dependency management. To set up the development environment:

```bash
# Install dependencies and create venv
uv sync

# Install with dev dependencies
uv sync --extra dev
```

Alternatively, you can use a standard virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"
```

## Important Notes

- **Always keep `ai-instructions.md` up to date with new functionality**. New updates should go into `ai-updates.md`.
- **Work is planned and tracked through the three-role phase system** — start at [`light-s3-client.md`](light-s3-client.md) (overview + phase index) and follow [`plan/working-agreement.md`](plan/working-agreement.md). The old `ai-tasks.md` has been retired.

## Supported Functions

### 1. `download_file(Bucket, Key, Filename)`
Downloads an S3 object to a local file.

**Parameters:**
- `Bucket` (str): The name of the bucket to download from
- `Key` (str): The name of the key to download from
- `Filename` (str): The path to the file to download to

### 2. `upload_fileobj(Fileobj, Bucket, Key)`
Uploads a file object to S3.

**Parameters:**
- `Fileobj` (file-like object): A file-like object to upload (must implement read method and return bytes)
- `Bucket` (str): The name of the bucket to upload to
- `Key` (str): The name of the key to upload to

### 3. `delete_file(Bucket, Key)`
Deletes an S3 object.

**Parameters:**
- `Bucket` (str): The name of the bucket to delete from
- `Key` (str): The name of the key to delete

### 4. `list_objects(Bucket, Prefix)`
Lists all keys in an S3 bucket with a given prefix.

**Parameters:**
- `Bucket` (str): The name of the bucket to list objects from
- `Prefix` (str): The prefix to use for filtering keys

### 5. `get_object(Bucket, Key)`
Checks if an S3 object exists.

**Parameters:**
- `Bucket` (str): The name of the bucket to check
- `Key` (str): The key to check for existence

### 6. `upload_file_multipart(Fileobj, Bucket, Key, part_size, max_parts)`
Upload a file to S3 using multipart upload for large files. Falls back to regular upload if the file is smaller than `part_size`.

**Parameters:**
- `Fileobj` (file-like object): A file-like object or bytes to upload
- `Bucket` (str): The name of the bucket to upload to
- `Key` (str): The name of the key to upload to
- `part_size` (int, optional): Size of each part in bytes. Default is 5MB (5242880)
- `max_parts` (int, optional): Maximum number of parts allowed. Default is 10000

### 7. `head_object(Bucket, Key)`
Checks if an S3 object exists and returns its metadata.

**Parameters:**
- `Bucket` (str): The name of the bucket to check
- `Key` (str): The key to check for existence and retrieve metadata

### 8. `put_object_tagging(Bucket, Key, Tags)`
Sets tags for an S3 object.

**Parameters:**
- `Bucket` (str): The name of the bucket
- `Key` (str): The key of the object to tag
- `Tags` (dict): Dictionary of tag key-value pairs

### 9. `get_object_tagging(Bucket, Key)`
Retrieves tags for an S3 object.

**Parameters:**
- `Bucket` (str): The name of the bucket
- `Key` (str): The key of the object to retrieve tags for

### 10. `create_bucket(Bucket)`
Creates an S3 bucket.

**Parameters:**
- `Bucket` (str): The name of the bucket to create

**Returns:** `True` on 200, `False` on `AccessDeniedToBucket`

### 11. `delete_bucket(Bucket)`
Deletes an S3 bucket.

**Parameters:**
- `Bucket` (str): The name of the bucket to delete

**Returns:** `True` on 204, `False` on `BucketNotFound`

### 12. `head_bucket(Bucket)`
Checks if an S3 bucket exists.

**Parameters:**
- `Bucket` (str): The name of the bucket to check

**Returns:** `True` on 200, `False` on `BucketNotFound`

## Client Initialization Parameters

| Property | Required | Type   | Default | Description |
|----------|----------|--------|---------|-------------|
| region   | True     | string | | The S3 region being used |
| access_key | True   | string | | The AWS Access Key for API Access |
| secret_key | True   | string | | The AWS Secret Key for API Access |
| server   | False    | string | None | An override of the HTTPS URL to use |
| encryption | False  | string | "AES256" | The encryption algorithm to use for uploads |
| signature_version | False | string | "v4" | AWS signature version to use ("v2" or "v4") |

## Authentication

The client implements AWS Signature Version 4 authentication by default, following the same standard as boto3. It handles the creation of authorization signatures required for S3 REST API requests. Legacy Signature Version 2 is also supported via the `signature_version="v2"` init parameter.

## Error Handling

The client raises specific exceptions (all inherit from `S3Error`):
- `S3Error`: Base exception class for all S3-related errors
- `BucketNotFound`: When a bucket cannot be found
- `AccessDeniedToBucket`: When access to a bucket is denied
- `UnknownBucketError`: For other bucket-related errors

## Usage Examples

### Basic Usage
```python
from light_s3_client import Client

s3 = Client(
    region="us-west-1",
    access_key="REPLACE_ME",
    secret_key="REPLACE_ME"
)

# Download a file
s3.download_file("mybucket", "hello.txt", "/tmp/hello.txt")

# Upload a file
with open("local_file.txt", "rb") as f:
    s3.upload_fileobj(f, "mybucket", "uploaded_file.txt")

# List objects
keys = s3.list_objects("mybucket", "prefix/")

# Check if object exists
exists = s3.get_object("mybucket", "path/file.txt")
```

## Build Workflow

### Development Setup
1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Testing
Run tests using pytest:
```bash
pytest
```

### Code Quality
- Linting: `flake8`
- Formatting: `black`

### Publishing
The project uses Hatch for building and publishing:
```bash
# Build the package
hatch build

# Publish to PyPI (requires proper credentials)
hatch publish
```

## CI/CD Workflows (GitHub Actions)

Three workflows live in `.github/workflows/`:

### 1. Version Check (`version-check.yml`)
- **Trigger:** Pull requests (opened, synchronize, ready_for_review) that touch `light-s3-client/**` or `pyproject.toml`
- **What it does:** Compares `__version__` in `light_s3_client/version.py` on the PR branch vs `origin/main`. Fails if the PR version is not strictly greater than main.
- **PR Comment:** Posts/updates a bot comment on failure; deletes it when the check passes.

### 2. PR Preview / Pre-release (`python-publish-test.yml`)
- **Trigger:** Pull requests (opened, synchronize, ready_for_review)
- **What it does:**
  1. Runs `.hooks/sync_version.py --dev` to auto-generate a `.devN` version (e.g. `0.0.34.dev3`) that doesn't collide with existing Test PyPI versions.
  2. Builds the package with `hatch build`.
  3. Publishes to **Test PyPI** using trusted publishing (`pypa/gh-action-pypi-publish` with `repository-url: https://test.pypi.org/legacy/`).
  4. Comments on the PR with install instructions:
     ```bash
     pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple light-s3-client==<version>
     ```

### 3. Release (`python-publish.yml`)
- **Trigger:** GitHub Release published
- **What it does:**
  1. Validates that the git tag matches the `hatch version` output (e.g. tag `v0.0.34` must match version `0.0.34`).
  2. Checks if the version already exists on PyPI (skips publish if so).
  3. Builds the package with `hatch build`.
  4. Publishes to **PyPI** using trusted publishing (`pypa/gh-action-pypi-publish`).
  5. Verifies the package is installable from PyPI (retries up to 30 times with 20s intervals).

### Release Process Summary

**Pre-release (automatic on PR):**
1. Open/update a PR → `version-check.yml` ensures version is bumped.
2. `python-publish-test.yml` auto-generates a `.devN` version and publishes to Test PyPI.
3. PR comment provides install command for testing.

**Production release:**
1. Bump `__version__` in `light_s3_client/version.py`.
2. Merge PR to main.
3. Create a GitHub Release with tag matching the version (e.g. `v0.0.34`).
4. `python-publish.yml` builds and publishes to PyPI, then verifies installability.

### Version Hook (`.hooks/sync_version.py`)
- Used by the PR Preview workflow with `--dev` flag.
- In `--dev` mode: if the version hasn't changed from HEAD, auto-generates the next available `.devN` version by querying Test PyPI.
- Without `--dev`: bumps the patch version if unchanged and exits with error (for local pre-commit use).

## Dependencies

### Required Dependencies
- `requests~=2.31.0`
- `xmltodict~=0.13.0`

### Development Dependencies
- `pytest`
- `pytest-cov`
- `black`
- `flake8`
- `python-dotenv`

## Project Structure

```
light-s3-client/
├── light_s3_client/
│   ├── __init__.py     # Main client implementation
│   ├── exceptions.py   # Custom exception classes
│   └── version.py      # Version information
├── tests/
│   └── test_integration.py  # Integration tests
├── pyproject.toml      # Project configuration
├── README.rst          # Documentation
└── LICENSE             # License information
```

## Implementation Details

The client implements direct S3 REST API calls using:
1. **AWS Signature Version 4**: For authenticating requests
2. **Requests library**: For making HTTP requests
3. **xmltodict**: For parsing XML responses from S3
4. **Custom error handling**: For specific S3 error conditions

The implementation follows AWS documentation for signature creation and handles the necessary headers and authentication for S3 API calls.

## Development Workflow

For development tasks and tracking, please refer to:
- `light-s3-client.md` - Project overview + phase index (entry point for all AI sessions)
- `plan/` - Working agreement, architecture reference, phase files, and defect register
- `ai-updates.md` - Session changelog of completed updates and changes