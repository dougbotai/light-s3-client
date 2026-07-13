# Phase dacoburn-15: Workflow-owned releases — retire local version bumping, add regression-gated release pipeline

> **Status:** planned — ready to implement
> **Depends on:** dacoburn-13 (MinIO CI service pattern for the regression gate)
> **Read first:** [architecture.md](../architecture.md), [working-agreement.md](../working-agreement.md)
> Work ONLY on this phase. Touch ONLY the files in its **Files** list.

**Goal:** Make the PR + release process multi-committer friendly. Today every PR must bump
`__version__` locally (enforced by `version-check.yml` and the `.hooks` pre-commit hook), which
guarantees merge conflicts on `version.py`/`pyproject.toml` the moment two people have PRs
open. Invert the model: **PRs never touch version files**; versioning happens only inside a
release workflow that first runs the full regression suite (unit + MinIO integration), then
bumps, tags, and publishes.

**Target state:**

```
PR:       unit tests + MinIO integration tests + "version freeze" check (fails if the PR
          touches version.py / pyproject version) + Test PyPI .devN preview (unchanged,
          version computed IN the workflow)
Release:  manually dispatched release.yml → regression gate (unit + integration) →
          bump version (patch/minor/major input) → commit to main → tag vX.Y.Z →
          GitHub Release → existing python-publish.yml publishes to PyPI (unchanged)
```

> **Phase-rules deviations, agreed at planning time:** (a) this phase touches 5 workflow/hook
> files — allowed because it is config-only, zero library code; (b) it adds no unit tests, so
> the final test count must **EQUAL** the Step 0 baseline (not exceed it) — the verifier
> checks equality.

## Step 0 — lifecycle (before any code)

- [ ] `git add -A && git commit -m "pre dacoburn-15: baseline"`; paste `git log --oneline -1`
- [ ] `python -m pytest tests/test_unit.py -q` — record the baseline test count in `ai-updates.md` (final count must EQUAL it)

## Implementation

### 1. Invert `version-check.yml` → version freeze

- [ ] Rework `.github/workflows/version-check.yml`: display name "Version Freeze"; on
      `pull_request` (opened, synchronize, ready_for_review) it **fails if the PR changes**
      the `__version__` line in `light_s3_client/version.py` or the `version =` line in
      `pyproject.toml` (compare against `origin/main` with `git diff origin/main...HEAD --`
      on those two paths). Keep the existing bot-comment pattern: post/update a comment
      explaining that versions are release-workflow-owned when the check fails; delete the
      comment when it passes.
  - Acceptance: `grep -n "Version Freeze" .github/workflows/version-check.yml` and
    `grep -cn "greater than\|is not strictly greater\|must be bumped" .github/workflows/version-check.yml` → 0 (old logic gone); paste both

### 2. Retire local version bumping

- [ ] Delete `.hooks/pre-commit`; `README-dev.md` no longer instructs
      `git config core.hooksPath .hooks` (section replaced by a note that versioning is
      workflow-owned)
  - Acceptance: `git ls-files .hooks/pre-commit` → empty, and
    `grep -c "core.hooksPath" README-dev.md` → 0; paste both
- [ ] `.hooks/sync_version.py`: the `--dev` mode (used by `python-publish-test.yml` to compute
      `.devN` versions **inside the workflow**) stays; invoking it **without** `--dev` now
      prints an error pointing at the release workflow and exits non-zero (no local bumping
      path left)
  - Acceptance: `python .hooks/sync_version.py; echo "exit=$?"` → error message + `exit=1`; paste
    (and `grep -n "\-\-dev" .github/workflows/python-publish-test.yml` still hits)

### 3. New `release.yml` — regression-gated release

- [ ] Create `.github/workflows/release.yml`, trigger `workflow_dispatch` with input
      `bump` (choice: `patch` | `minor` | `major`, default `patch`), runnable only on the
      default branch. **Job 1 `regression`:** MinIO service container (same image/health-check
      pattern as `minio-integration-tests.yml`), then `python -m pytest tests/test_unit.py -q`
      AND `python -m pytest tests/test_integration.py -v` — any failure stops the release.
  - Acceptance: `grep -n "workflow_dispatch" .github/workflows/release.yml`,
    `grep -n "patch" .github/workflows/release.yml`, and
    `grep -n "minio" .github/workflows/release.yml`; paste all three
- [ ] **Job 2 `release` (`needs: regression`):** reads the current `__version__` from
      `light_s3_client/version.py`, bumps it per the `bump` input, writes the new version to
      BOTH `light_s3_client/version.py` and `pyproject.toml`, commits to main as the
      github-actions bot with message `release: v<new-version>`, tags `v<new-version>`,
      pushes commit + tag, and creates a GitHub Release for the tag (`gh release create
      --generate-notes`). The existing `python-publish.yml` (trigger: release published)
      remains the publish step unchanged — its tag↔version validation now always passes by
      construction.
  - Acceptance: `grep -n "needs: regression" .github/workflows/release.yml`,
    `grep -n "gh release create" .github/workflows/release.yml`, and
    `git diff --stat -- .github/workflows/python-publish.yml` → no changes; paste all three
- [ ] Both new/reworked workflows are valid YAML:
      `python -c "import tomllib" 2>/dev/null; python - <<'EOF'` … (if PyYAML is unavailable
      in the dev env, acceptance is instead: push the branch and paste the Actions run/lint
      result, or `pip install pyyaml` in the venv and parse both files —
      `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/release.yml')); yaml.safe_load(open('.github/workflows/version-check.yml')); print('YAML OK')"`)
  - Acceptance: paste `YAML OK` (or the green Actions lint evidence)

### 4. Unit tests on every PR

- [ ] Add a `unit-tests` job to `.github/workflows/minio-integration-tests.yml` (no MinIO
      service needed) running `python -m pytest tests/test_unit.py -q`, so every PR gets the
      offline suite even when integration is red/skipped
  - Acceptance: `grep -n "unit-tests" .github/workflows/minio-integration-tests.yml` and
    `grep -n "test_unit" .github/workflows/minio-integration-tests.yml`; paste both

### 5. Documentation

- [ ] `README-dev.md`: "How to Release" rewritten — releasing = run the **Release** workflow
      from the Actions tab with a bump type; PRs that touch version files fail the freeze
      check; local hook setup section removed. `ai-instructions.md` CI/CD section updated to
      match (four workflows: version freeze, PR preview, minio+unit tests, release).
  - Acceptance: `grep -c "workflow_dispatch\|Release workflow\|Actions tab" README-dev.md` → ≥1
    and `grep -c "Version Freeze\|version freeze" ai-instructions.md` → ≥1; paste both

## Files

`.github/workflows/version-check.yml`, `.github/workflows/release.yml` (new),
`.github/workflows/minio-integration-tests.yml`, `.hooks/pre-commit` (deleted),
`.hooks/sync_version.py` *(5 config files — allowed, config-only phase; ZERO files under
`light_s3_client/` or `tests/` may change)* + docs ride-along: `README-dev.md`,
`ai-instructions.md`.

**Human follow-ups (not machine-checkable, out of checklist):** enable branch protection on
`main` requiring the `unit-tests` + integration + freeze checks; optionally restrict who can
dispatch `release.yml` via an environment protection rule; grant the workflow
`contents: write` permission via the repo's Actions settings if the default token is
read-only.

## Step Z — lifecycle (after all code)

- [ ] `git status --porcelain -- light_s3_client/ tests/` → empty (no library/test code touched); paste
- [ ] `python -m pytest tests/test_unit.py -q` — count EQUALS the Step 0 baseline, all green; paste FULL output
- [ ] `git add -A && git commit -m "dacoburn-15: workflow-owned releases"`; paste `git log --oneline -1`
- [ ] Set this file's Status + the index row in `light-s3-client.md` to `awaiting verification`. Do NOT touch `plan/defects.md`

**Acceptance (verification session):** freeze check fails-on-version-change semantics confirmed
by reading the workflow diff (attack: does it still require a bump anywhere?); `.hooks/pre-commit`
gone and no `core.hooksPath` instruction remains; `release.yml` regression job runs BOTH suites
and the release job is `needs:`-gated on it; `python-publish.yml` untouched; no file under
`light_s3_client/` or `tests/` changed; unit count equals baseline;
`git diff -- plan/ light-s3-client.md` shows only this phase's checkbox flips + Status.
