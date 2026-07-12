# Development Testing Information

This document contains information about testing for developers working on the light-s3-client library.

## Development Setup

This project uses `uv` for dependency management. To set up the development environment:

```bash
# Install dependencies and create venv
uv sync

# Install with dev dependencies
uv sync --extra dev
```

Alternatively, you can use pip with a virtual environment:

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

## Pre-commit Hook Setup

The project includes a version-check pre-commit hook that prevents commits without a version bump. To enable it, point git to the `.hooks` directory:

```bash
git config core.hooksPath .hooks
```

This works on Windows, macOS, and Linux (Git for Windows includes the bash shell needed to run the hook).

**What the hook does:** On commit, it compares `__version__` in `light_s3_client/version.py` against the last committed version. If unchanged, it auto-bumps the patch version, updates `version.py` and `pyproject.toml`, and **aborts the commit** so you can `git add` the version files and commit again.

## Running Tests

To run all tests, you can use the following methods:

1. Run all tests using pytest directly:
   ```bash
   pytest tests/
   ```

2. Run the test runner script:
   ```bash
   python run_tests.py
   ```

3. For integration testing, you'll need to set up a test environment with S3 credentials or use the provided Docker Compose setup for MinIO testing:
   ```bash
   docker-compose up -d
   ```

### Running Integration Tests

Integration tests run against a real MinIO S3-compatible server. You can run them locally or they run automatically in CI.

**Local run:**
1. Start MinIO via Docker Compose:
   ```bash
   docker-compose up -d
   ```
2. Run integration tests (MinIO listens on port 5000 locally):
   ```bash
   S3_SERVER=http://localhost:5000 pytest tests/test_integration.py -v
   ```
   (Credentials default to `minioadmin`/`minioadmin`.)

**CI run:**
Integration tests run automatically on every push to `main`/`master` and on pull requests via `.github/workflows/minio-integration-tests.yml`. The workflow spins up a MinIO service, creates a unique test bucket per run, executes tests, and cleans up the bucket (even on failure, via `if: always()`).

**Running unit tests only:**
```bash
pytest tests/test_unit.py
```
or skip integration tests anywhere:
```bash
pytest -m "not integration"
```

**Running integration tests only:**
```bash
pytest -m integration
```

## Development Dependencies

For development, install with dev extras:
```bash
uv sync --extra dev
```

Or with pip:
```bash
pip install -e ".[dev]"
```

This will install pytest, pytest-cov, black, flake8, and python-dotenv which are needed for development and testing.

## CI/CD Workflows (GitHub Actions)

Three workflows automate version checking, pre-release previews, and production releases.

### Version Check (on PR)

Runs on PRs that touch source code or `pyproject.toml`. Compares `__version__` in `light_s3_client/version.py` against `origin/main` and **fails if the version is not incremented**. Posts/removes a bot comment on the PR accordingly.

### PR Preview / Pre-release (on PR)

Automatically publishes a `.devN` pre-release to **Test PyPI** on every PR update:

1. `.hooks/sync_version.py --dev` generates a unique `.devN` version (e.g. `0.0.34.dev3`).
2. Builds and publishes to Test PyPI via trusted publishing.
3. Comments on the PR with install instructions:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple light-s3-client==<version>
   ```

### Production Release (on GitHub Release)

Triggered when a GitHub Release is published:

1. Validates the git tag matches `hatch version` (e.g. tag `v0.0.34` ↔ version `0.0.34`).
2. Skips if the version already exists on PyPI.
3. Builds and publishes to **PyPI** via trusted publishing.
4. Verifies the package is pip-installable (retries for up to 10 minutes).

### How to Release

**Pre-release (automatic):**
- Open or update a PR. The preview package is published to Test PyPI automatically.

**Production release:**
1. Bump `__version__` in `light_s3_client/version.py`.
2. Merge PR to main.
3. Create a GitHub Release with a tag matching the version (e.g. `v0.0.34`).
4. The workflow publishes to PyPI and verifies installability.