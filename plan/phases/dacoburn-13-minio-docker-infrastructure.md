# Phase dacoburn-13: MinIO Docker Infrastructure for CI/CD and Local Testing

> **Status:** awaiting verification
> **Depends on:** —
> **Read first:** [architecture.md](../architecture.md), [working-agreement.md](../working-agreement.md)
> Work ONLY on this phase. Touch ONLY the files in its **Files** list.

**Goal:** Set up MinIO as a Docker service that runs automatically in GitHub Actions AND locally
via `docker-compose.yml`, so every future phase can run integration tests against a real
S3-compatible backend. Provide unique-per-run test buckets that are cleaned up after tests.

This phase creates the infrastructure — no feature code changes. Integration tests are not a
phase acceptance gate (per working-agreement rule 3), but this phase makes them runnable.

## Step 0 — lifecycle (before any code)

- [ ] `git add -A && git commit -m "pre dacoburn-13: baseline"`; paste `git log --oneline -1`
- [ ] `python -m pytest tests/test_unit.py -q` — record the baseline test count in `ai-updates.md`
      (final count must EXCEED it)

## Implementation

### 1. GitHub Actions workflow

- [ ] Create `.github/workflows/minio-integration-tests.yml` that:
  - Runs on `push` to `main`/`master` AND on `pull_request` (opened/synchronize)
  - Starts MinIO as a GitHub Actions Docker service with health checks (`curl` to
    `/minio/health/live`, interval 10s, timeout 5s, retries 10)
  - Sets up Python 3.11 (a version in the supported range 3.8–3.13)
  - Installs dependencies (`hatch env create dev` + `pip install python-dotenv`)
  - Creates a **unique test bucket** at start (using `mc` CLI aliased to `localhost:9000`)
  - Sets env vars `s3_server=http://localhost:9000`, `s3_access_key=minioadmin`,
    `s3_secret_key=minioadmin`, `s3_bucket=<unique-name>`, `s3_region=us-east-1`
  - Runs `pytest tests/test_integration.py -v --tb=long`
  - **Deletes the test bucket at the end** (in a `if: always()` step so cleanup runs
    even on failure)
  - Acceptance: `cat .github/workflows/minio-integration-tests.yml | grep -c "minio/minio"` → ≥1; paste
  - Acceptance: `cat .github/workflows/minio-integration-tests.yml | grep -c "if: always"` → ≥1 (cleanup); paste

### 2. Pytest integration marker

- [ ] Add `pytest.mark.integration` marker to `pyproject.toml` `[tool.pytest.ini_options]`
      (or a `pytest.ini`/`conftest.py` if none exists) so `pytest -m "not integration"` skips
      MinIO tests, and marker warnings are suppressed
  - Acceptance: `grep -n "integration" pyproject.toml` or `grep -rn "register" tests/conftest.py`; paste

- [ ] Ensure every existing test in `tests/test_integration.py` is decorated with
      `@pytest.mark.integration` (or that the marker applies to the whole module)
  - Acceptance: `grep -c "pytest.mark.integration\|mark.integration" tests/test_integration.py`; paste

### 3. Docker Compose verification

- [ ] Verify the existing `docker-compose.yml` is compatible with the CI setup (same
      credentials `minioadmin`/`minioadmin`, same ports mapped locally as 5000:9000), and
      confirm the integration tests can connect to it with env vars
      `s3_server=http://localhost:5000`
  - Acceptance: `grep -c "minioadmin" docker-compose.yml` → ≥2 (user + password); paste

### 4. Documentation

- [ ] Update `README-dev.md` with a section "Running Integration Tests" covering:
  - Local run: `docker-compose up -d` then `pytest tests/test_integration.py` (or with env
    vars `s3_server=http://localhost:5000`)
  - CI run: automatic on push/PR via `minio-integration-tests.yml`
  - How to run unit tests only: `pytest tests/test_unit.py` or `pytest -m "not integration"`
  - How to run integration tests only: `pytest -m integration`
  - Acceptance: `grep -c "docker-compose" README-dev.md` → ≥1; paste
  - Acceptance: `grep -c "integration" README-dev.md` → ≥1; paste

## Files

`.github/workflows/minio-integration-tests.yml`, `pyproject.toml`, `tests/test_integration.py`
(3 code files) + docs ride-along: `README-dev.md`, `docker-compose.yml` (verify only, no changes unless needed).

## Step Z — lifecycle (after all code)

- [ ] `cat .github/workflows/minio-integration-tests.yml` exists and contains `minio/minio`
      service, `if: always` cleanup step, and runs on push + PR; paste `cat` output
- [ ] `grep -n "integration" pyproject.toml` shows marker registration; paste
- [ ] `python -m pytest tests/test_integration.py --collect-only -q 2>&1 | grep -i "mark\|integration\|collected"` — confirm integration tests are collected; paste
- [ ] `python -m pytest tests/test_unit.py -q` — count EXCEEDS Step 0 baseline; paste FULL output
- [ ] Docs: `grep -c "integration" README-dev.md` → ≥1; paste
- [ ] `git add -A && git commit -m "dacoburn-13: MinIO Docker infrastructure"`; paste `git log --oneline -1`
- [ ] Set this file's Status + the index row in `light-s3-client.md` to `awaiting verification`. Do NOT touch `plan/defects.md`

**Acceptance (verification session):** the workflow file exists with MinIO service, health
check, unique bucket creation, cleanup in `if: always`, push+PR triggers; the pytest marker
is registered and suppresses warnings; `README-dev.md` has a "Running Integration Tests"
section with local + CI instructions; `docker-compose.yml` is compatible;
`git diff -- plan/ light-s3-client.md` shows only this phase's checkbox flips + Status.
