# light-s3-client — Project Plan & Phase Index

> **Start here for any AI/automation session.** This file is the overview + the phase index.
> The rules for how work moves are in [`plan/working-agreement.md`](plan/working-agreement.md);
> the stack, module layout, and invariants are in [`plan/architecture.md`](plan/architecture.md);
> found defects live in [`plan/defects.md`](plan/defects.md); per-phase task files are in
> [`plan/phases/`](plan/phases/). This system replaces the old `ai-tasks.md`.

## Overview

`light-s3-client` is a lightweight Python library for talking to Amazon S3 (and S3-compatible
services such as MinIO) via the REST API directly — only `requests` + `xmltodict`, no boto3.
It implements AWS Signature V4 (V2 legacy) itself and mirrors boto3's method/parameter naming
(`Bucket`, `Key`, …) without pulling in the SDK.

**Current capabilities:** object download/upload (incl. multipart), delete, list (single page),
existence check, head, object tagging. **Goal of this plan:** grow it into a fully functional
standalone client for all routine S3 management — bucket lifecycle, pagination, content
retrieval, copy/batch operations, presigned URLs, versioning, tagging/policy/CORS/ACLs, and a
hardened transport — one narrow, verifiable phase at a time.

## This project uses a THREE-ROLE workflow

Work moves through three **separate sessions**, each a distinct role. The model that writes
code never certifies its own work.

1. **PLANNER** — cuts one single-session phase into `plan/phases/`; keeps this index and
   `plan/architecture.md` current. Writes no code.
2. **IMPLEMENTER** — implements exactly one planned phase, touching only its listed files; ends
   at `awaiting verification`. **Never self-certifies `✅ complete`.**
3. **VERIFIER** — fresh context, ideally a different model; adversarial: reproduces every pasted
   output, diffs `plan/`, attacks the invariants. Only role that sets `✅ complete`; owns
   `plan/defects.md`.

Full rules: [`plan/working-agreement.md`](plan/working-agreement.md).

Statuses: `needs plan` → `planned — ready to implement` → `awaiting verification` →
`✅ complete (verified)` / `⚠️ verification failed`.

## Phase naming convention (multi-committer safe)

Phases are named **`<github-account>-<number>`** (e.g. `dacoburn-3`), and phase files are
`plan/phases/<github-account>-<number>-<slug>.md`. Each committer numbers their own phases
sequentially under their own GitHub account name, so parallel committers never clash on phase
IDs or file names. When cutting a new phase, take the next unused number **for your account**.

## Phase index

| Phase | Task | Status | Depends on |
|-------|------|--------|------------|
| [dacoburn-1](plan/phases/dacoburn-1-bucket-management-core.md) | Bucket management core: `create_bucket`, `delete_bucket`, `head_bucket` | awaiting verification | — |
| [dacoburn-2](plan/phases/dacoburn-2-list-buckets-and-pagination.md) | `list_buckets` + `list_objects` pagination (continuation tokens, `MaxKeys`) | planned — ready to implement | — |
| [dacoburn-3](plan/phases/dacoburn-3-get-object-content.md) | `get_object` content retrieval + `download_fileobj` (keep existence check as `object_exists`) | planned — ready to implement | — |
| [dacoburn-4](plan/phases/dacoburn-4-copy-and-batch-delete.md) | `copy_object` + `delete_objects` (batch delete up to 1000 keys) | planned — ready to implement | dacoburn-3 |
| [dacoburn-5](plan/phases/dacoburn-5-key-encoding-and-metadata.md) | Key URL-encoding correctness + user metadata (`x-amz-meta-*`) on uploads | planned — ready to implement | dacoburn-4 |
| [dacoburn-6](plan/phases/dacoburn-6-presigned-urls.md) | `generate_presigned_url` (SigV4 query-string signing, GET/PUT) | planned — ready to implement | dacoburn-5 |
| [dacoburn-7](plan/phases/dacoburn-7-tagging-completeness.md) | Tagging completeness: `delete_object_tagging` + bucket tagging (get/put/delete) | planned — ready to implement | dacoburn-1, dacoburn-4 |
| [dacoburn-8](plan/phases/dacoburn-8-versioning.md) | Versioning: bucket versioning get/put, `list_object_versions`, `VersionId` support | planned — ready to implement | dacoburn-2, dacoburn-3 |
| [dacoburn-9](plan/phases/dacoburn-9-multipart-management.md) | Multipart management: `list_multipart_uploads`, `list_parts`, public `abort_multipart_upload` | planned — ready to implement | — |
| [dacoburn-10](plan/phases/dacoburn-10-transport-hardening.md) | Transport hardening: timeouts + retry with backoff in `do_request` | planned — ready to implement | — |
| [dacoburn-11](plan/phases/dacoburn-11-bucket-policy-and-cors.md) | Bucket policy (get/put/delete) + CORS (get/put/delete) | planned — ready to implement | dacoburn-1, dacoburn-4 |
| [dacoburn-12](plan/phases/dacoburn-12-acls.md) | ACLs: canned ACLs, `get/put_object_acl`, `get/put_bucket_acl` | planned — ready to implement | dacoburn-1, dacoburn-4 |
| [dacoburn-13](plan/phases/dacoburn-13-minio-docker-infrastructure.md) | MinIO Docker infrastructure: CI/CD workflow + local docker-compose for integration tests | planned — ready to implement | — |
| [dacoburn-14](plan/phases/dacoburn-14-full-integration-test-suite.md) | Full integration test suite against MinIO: regression tests for all public Client methods | planned — ready to implement | dacoburn-13 |

## Ordering

Dependency-ordered, but independent phases may be taken in parallel by different committers
(one phase per session, always). Suggested order for a single committer:
**1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.** Foundations first (buckets,
pagination, content retrieval), then correctness (encoding/metadata), then the wider S3
management surface. Phases **13 → 14** (MinIO infrastructure + integration tests) are
independent and can be run in parallel with any feature phase, but 14 requires 13 first.

## Where to look

| What | Where |
|------|-------|
| Rules for all three roles | [`plan/working-agreement.md`](plan/working-agreement.md) |
| Stack, module layout, invariants every phase must preserve | [`plan/architecture.md`](plan/architecture.md) |
| Per-phase task files | [`plan/phases/`](plan/phases/) |
| Defect register (verifier-owned) | [`plan/defects.md`](plan/defects.md) |
| Session changelog (every session appends, newest on top) | [`ai-updates.md`](ai-updates.md) |
| Library API reference for AI sessions | [`ai-instructions.md`](ai-instructions.md) |
| Dev setup, tests, CI/CD, release process | [`README-dev.md`](README-dev.md) |

## Revision history

- **2026-07-11:** Plan system created on branch `improvement/add-ai-automation-plans`.
  `ai-tasks.md` retired (all its items were already completed and summarized in
  `ai-updates.md`). Twelve phases cut from a gap analysis of the current client vs. a fully
  functional standalone S3 management client.
