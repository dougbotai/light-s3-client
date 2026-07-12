# Phase dacoburn-1: Bucket management core — create_bucket, delete_bucket, head_bucket

> **Status:** awaiting verification
> **Depends on:** —
> **Read first:** [architecture.md](../architecture.md), [working-agreement.md](../working-agreement.md)
> Work ONLY on this phase. Touch ONLY the files in its **Files** list.

**Goal:** The client can create, delete, and existence-check buckets — the minimum for
standalone S3 management (today it can only operate inside pre-existing buckets).

> This file is the **format to copy** for later phases: Step 0 baseline, checklist items that
> each carry an acceptance command, named tests, a Files list, and a close-out step.

## Step 0 — lifecycle (before any code)

- [ ] `git add -A && git commit -m "pre dacoburn-1: baseline"`; paste `git log --oneline -1`
- [ ] `python -m pytest tests/test_unit.py -q` — record the baseline test count in `ai-updates.md` (final count must EXCEED it)

## Implementation

Exact signatures (boto3 naming — copy, don't invent). All three live in
`light_s3_client/buckets/__init__.py`, all HTTP via `self.do_request`, all signing via
`self.create_aws_signature`:

- [ ] `def create_bucket(self, Bucket: str) -> bool` — `PUT {server}/{Bucket}`. When
      `self.region != "us-east-1"`, send a `CreateBucketConfiguration` body with
      `LocationConstraint` = `self.region`, built with `xmltodict.unparse` (invariant: no
      string-templated XML); pass the body bytes as `payload` to `create_aws_signature` so the
      V4 payload hash covers it. Returns `True` on 200, `False` on `AccessDeniedToBucket`.
  - Acceptance: `grep -n "def create_bucket" light_s3_client/buckets/__init__.py` and
    `grep -n "xmltodict.unparse" light_s3_client/buckets/__init__.py` — paste both
- [ ] `def delete_bucket(self, Bucket: str) -> bool` — `DELETE {server}/{Bucket}`; `True` on
      204, `False` on `BucketNotFound` (bucket-not-empty errors propagate as
      `UnknownBucketError` — do not swallow them)
  - Acceptance: `grep -n "def delete_bucket" light_s3_client/buckets/__init__.py`
- [ ] `def head_bucket(self, Bucket: str) -> bool` — `HEAD {server}/{Bucket}`; `True` on 200,
      `False` on `BucketNotFound`
  - Acceptance: `grep -n "def head_bucket" light_s3_client/buckets/__init__.py`
- [ ] Binding pattern completed in `light_s3_client/__init__.py` for all three: `setattr`
      binding + `TYPE_CHECKING` stub with the exact signatures above
  - Acceptance: `grep -n "create_bucket\|delete_bucket\|head_bucket" light_s3_client/__init__.py` → 6 hits (3 stubs + 3 setattr); paste
- [ ] Named tests in `tests/test_unit.py`, offline via `unittest.mock` (mock at the
      `requests.request` level, exact-equality assertions):
  - [ ] `test_create_bucket_returns_true_on_200`: mocked 200 → `assert result is True`; the
        mocked call's URL == `f"{server}/{bucket}"` and method == `"PUT"` (exact)
  - [ ] `test_create_bucket_sends_location_constraint`: with `region="us-west-1"`, the request
        body parsed with `xmltodict.parse` yields
        `{"CreateBucketConfiguration": {"LocationConstraint": "us-west-1"}}` — assert the
        parsed dict contains exactly that LocationConstraint value
  - [ ] `test_delete_bucket_returns_true_on_204`: mocked 204 → `assert result is True`
  - [ ] `test_head_bucket_false_when_missing`: mocked 404 → `assert result is False` (no
        exception escapes)

## Files

`light_s3_client/buckets/__init__.py`, `light_s3_client/__init__.py`, `tests/test_unit.py`
(3 code files) + docs ride-along: `README.md`, `ai-instructions.md`.

## Step Z — lifecycle (after all code)

- [ ] `python -m pytest tests/test_unit.py --collect-only -q | grep -cE "test_create_bucket_returns_true_on_200|test_create_bucket_sends_location_constraint|test_delete_bucket_returns_true_on_204|test_head_bucket_false_when_missing"` → 4; paste
- [ ] Full `python -m pytest tests/test_unit.py -q` — count EXCEEDS the Step 0 baseline; paste FULL output
- [ ] Docs updated: `grep -c "create_bucket" README.md ai-instructions.md` → ≥1 in each; paste
- [ ] `git add -A && git commit -m "dacoburn-1: bucket management core"`; paste `git log --oneline -1`
- [ ] Set this file's Status + the index row in `light-s3-client.md` to `awaiting verification`. Do NOT touch `plan/defects.md`

**Acceptance (verification session):** the 4 named tests collected and green; all three methods
exist in the buckets module with the exact signatures; the binding grep shows 6 hits; the
CreateBucketConfiguration body goes through `xmltodict.unparse` and is passed as the signing
payload; `git diff -- plan/ light-s3-client.md` shows only this phase's checkbox flips + Status.
