# Phase dacoburn-14: Full Integration Test Suite Against MinIO

> **Status:** planned — ready to implement
> **Depends on:** dacoburn-13
> **Read first:** [architecture.md](../architecture.md), [working-agreement.md](../working-agreement.md)
> Work ONLY on this phase. Touch ONLY the files in its **Files** list.

**Goal:** Comprehensive regression test suite in `tests/test_integration.py` that exercises
**every** public `Client` method against real MinIO. Each test creates its own uniquely-named
bucket, exercises the function, verifies with exact assertions, and tears down. This catches
regressions that mocked unit tests cannot.

Per working-agreement rule 3, integration tests are never a phase acceptance gate — this phase
adds the tests and marks them `@pytest.mark.integration`. The acceptance gate is that the
**unit** test suite still passes and the integration tests collect and are runnable.

## Step 0 — lifecycle (before any code)

- [ ] `git add -A && git commit -m "pre dacoburn-14: baseline"`; paste `git log --oneline -1`
- [ ] `python -m pytest tests/test_unit.py -q` — record the baseline test count in `ai-updates.md`
      (final count must EXCEED it)

## Implementation

All tests live in `tests/test_integration.py` and are decorated `@pytest.mark.integration`.
Each test creates a unique bucket (e.g., `test-<func>-<uuid>`) at fixture/setup, and deletes
it at teardown. Tests connect via the env vars set by dacoburn-13.

### Client initialization and connection

- [ ] `test_client_initialization_minio`: Create a client pointing to localhost MinIO, verify
      `server` is set to the MinIO URL, `region` is `us-east-1`
  - Acceptance: `grep -n "def test_client_initialization_minio" tests/test_integration.py`

### Bucket operations

- [ ] `test_create_bucket_integration`: Create a new bucket, assert `True` returned, verify
      with `head_bucket` that it exists (`True`)
  - Acceptance: `grep -n "def test_create_bucket_integration" tests/test_integration.py`

- [ ] `test_head_bucket_exists_and_not_exists`: `head_bucket` on the created bucket → `True`;
      on a nonexistent bucket name → `False`
  - Acceptance: `grep -n "def test_head_bucket_exists_and_not_exists" tests/test_integration.py`

- [ ] `test_delete_bucket_integration`: Delete the bucket (empty), assert `True`; verify with
      `head_bucket` that it's gone (`False`); delete nonexistent bucket → `False`
  - Acceptance: `grep -n "def test_delete_bucket_integration" tests/test_integration.py`

### Object operations

- [ ] `test_upload_fileobj_and_download_roundtrip`: Upload a `BytesIO` with known content
      (e.g., `b"hello minio"`) to a key, then download to a temp file and assert the file
      contents match byte-for-byte (`assert downloaded == b"hello minio"`)
  - Acceptance: `grep -n "def test_upload_fileobj_and_download_roundtrip" tests/test_integration.py`

- [ ] `test_upload_fileobj_bytes`: Upload raw `bytes` (not BytesIO), download and verify
      content matches
  - Acceptance: `grep -n "def test_upload_fileobj_bytes" tests/test_integration.py`

- [ ] `test_upload_fileobj_bytearray`: Upload `bytearray`, download and verify content matches
  - Acceptance: `grep -n "def test_upload_fileobj_bytearray" tests/test_integration.py`

- [ ] `test_get_object_exists_and_not_exists`: `get_object` on uploaded key → `True`; on a
      nonexistent key → `False`
  - Acceptance: `grep -n "def test_get_object_exists_and_not_exists" tests/test_integration.py`

- [ ] `test_head_object_metadata`: Upload an object, call `head_object`, assert returned dict
      has `Content-Length` matching uploaded size, has `ETag` key present
  - Acceptance: `grep -n "def test_head_object_metadata" tests/test_integration.py`

- [ ] `test_head_object_not_exists`: `head_object` on nonexistent key → returns `{}` (empty dict)
  - Acceptance: `grep -n "def test_head_object_not_exists" tests/test_integration.py`

- [ ] `test_delete_file_integration`: Upload a file, verify it exists with `get_object` → `True`,
      delete it, verify `get_object` → `False`; delete already-deleted file → returns without error
  - Acceptance: `grep -n "def test_delete_file_integration" tests/test_integration.py`

### List objects

- [ ] `test_list_objects_empty_bucket`: On a fresh empty bucket with any prefix → returns `[]`
  - Acceptance: `grep -n "def test_list_objects_empty_bucket" tests/test_integration.py`

- [ ] `test_list_objects_multiple_with_prefix`: Upload 3 keys sharing a prefix (e.g.,
      `prefix/a`, `prefix/b`, `prefix/c`), call `list_objects` with that prefix, assert
      the result list contains all 3 keys (exact membership check)
  - Acceptance: `grep -n "def test_list_objects_multiple_with_prefix" tests/test_integration.py`

- [ ] `test_list_objects_nested_keys`: Upload keys with nested paths (e.g.,
      `folder/subfolder/file.txt`), verify they appear in list results
  - Acceptance: `grep -n "def test_list_objects_nested_keys" tests/test_integration.py`

### Multipart upload

- [ ] `test_upload_file_multipart_large`: Create data larger than 5MB (e.g., 10MB of
      repeating bytes), upload via `upload_file_multipart`, download and verify byte-for-byte
      match
  - Acceptance: `grep -n "def test_upload_file_multipart_large" tests/test_integration.py`

- [ ] `test_upload_file_multipart_small_fallback`: Upload data smaller than part_size (e.g.,
      1KB) via `upload_file_multipart`, verify it succeeds and content roundtrips (confirms
      fallback to regular upload)
  - Acceptance: `grep -n "def test_upload_file_multipart_small_fallback" tests/test_integration.py`

### Object tagging

- [ ] `test_put_and_get_object_tagging`: Upload an object, set tags via `put_object_tagging`
      (e.g., `{"env": "test", "owner": "ci"}`), retrieve via `get_object_tagging`, assert
      the returned dict equals the set tags exactly
  - Acceptance: `grep -n "def test_put_and_get_object_tagging" tests/test_integration.py`

- [ ] `test_get_object_tagging_no_tags`: On an object with no tags, `get_object_tagging`
      returns `{}` or raises appropriately (verify actual behavior)
  - Acceptance: `grep -n "def test_get_object_tagging_no_tags" tests/test_integration.py`

### Error handling

- [ ] `test_bucket_not_found_error`: Create client, attempt operation on a bucket that doesn't
      exist, verify `BucketNotFound` is raised (not swallowed)
  - Acceptance: `grep -n "def test_bucket_not_found_error" tests/test_integration.py`

### Named tests in `tests/test_unit.py` — update for new integration coverage

Per working-agreement, integration tests are NOT the acceptance gate. Add corresponding
offline unit tests in `tests/test_unit.py` for any gaps found:

- [ ] Verify unit test count EXCEEDS the Step 0 baseline (add any missing mocked tests
      if the integration test writing revealed uncovered code paths)
  - Acceptance: `python -m pytest tests/test_unit.py -q` — count EXCEEDS baseline; paste FULL output

## Files

`tests/test_integration.py` (major rewrite), `tests/test_unit.py` (add any missing mocked
tests), `README-dev.md` (update integration test documentation) (3 code files + docs ride-along).

## Step Z — lifecycle (after all code)

- [ ] `python -m pytest tests/test_integration.py --collect-only -q` — all integration tests
      collected (≥17 tests); paste output
- [ ] `python -m pytest tests/test_unit.py -q` — count EXCEEDS Step 0 baseline; paste FULL output
- [ ] Every integration test is decorated with `@pytest.mark.integration`; verify:
      `grep -c "pytest.mark.integration\|mark.integration" tests/test_integration.py`; paste
- [ ] `docker-compose up -d && python -m pytest tests/test_integration.py -v --tb=long 2>&1 | tail -30`
      — run against local MinIO; paste the last 30 lines showing results (tests should pass
      when MinIO is running)
- [ ] `git add -A && git commit -m "dacoburn-14: full integration test suite"`; paste `git log --oneline -1`
- [ ] Set this file's Status + the index row in `light-s3-client.md` to `awaiting verification`. Do NOT touch `plan/defects.md`

**Acceptance (verification session):** ≥17 integration tests collected, all marked
`@pytest.mark.integration`; unit test suite still green and count exceeds baseline;
integration tests pass when run against a live local MinIO (`docker-compose up -d`);
each test creates and tears down its own bucket; `git diff -- plan/ light-s3-client.md`
shows only this phase's checkbox flips + Status.
