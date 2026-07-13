# Working Agreement — Three-Role Coding-Model Workflow (light-s3-client)

This project is built by **three separate sessions, each a distinct role and (recommended) a
distinct model.** The roles never run concurrently in the same working tree; every session
commits its own edits before the next begins. This structure exists because coding models mark
work "done" that isn't: honesty and scope control have to be **mechanical**, not voluntary. The
model that writes code never certifies its own work.

**The phase index lives in [`../light-s3-client.md`](../light-s3-client.md)** (repo root), not
in `plan/`. Everywhere the rules below say "the index", that is the file meant.

## Phase naming (multi-committer safe)

Phases are IDs of the form **`<github-account>-<number>`** (e.g. `dacoburn-3`); phase files are
`plan/phases/<github-account>-<number>-<slug>.md`. Each committer numbers their own phases
sequentially under their own GitHub account name so parallel committers never clash. A planner
cutting a new phase takes the next unused number for the account it is planning for.

## Role → model mapping (guidance — adjust to the models you have)

- **Match the model to the phase.** A mid-capability coding model handles a well-scoped phase
  (≤ ~3 code files, concrete acceptance criteria) reliably. Reserve a large, long-context model
  for architecture work and for authoring precise phase files.
- **The implementer is the strongest coding model appropriate to the phase's difficulty;** the
  planner can share that model (separate session, separate context).
- **The verifier should be a DIFFERENT model from the implementer whenever you have one.**
  That independence is the whole point. Escalate a genuinely uncertain finding to your
  strongest model.
- **With only one model, still run three separate fresh sessions** and lean harder on the
  mechanical gate below.

## The loop

```
PLANNER (writes/updates ONE phase file)
   → IMPLEMENTER (builds exactly that phase → awaiting verification)
      → VERIFIER (adversarial → ✅ complete, OR ⚠️ failed + files a defect)
         → (on failure) back to PLANNER (remediation phase) or IMPLEMENTER
```

One phase moves through all three roles before the next starts **for that committer**.
Different committers may run independent phases in parallel (that is what the phase naming
convention is for), but never pipeline multiple phases through one role in one session.

---

## Role 1 — PLANNER

**Owns:** the phase index in `light-s3-client.md`, `plan/architecture.md`, `plan/phases/*.md`.
**Never writes app code, never writes tests, never ticks an implementation checkbox.**

1. `git add -A && git commit -m "pre-plan <phase>: baseline"`; paste `git log --oneline -1`.
2. Read `plan/architecture.md` + the relevant part of the phase index for the slice you cut.
3. Write **one** `plan/phases/<account>-<N>-<slug>.md` that carves a single-session slice:
   - It touches **≤ 3 code files** (docs updates — `README.md`, `ai-instructions.md` — ride
     along and don't count).
   - Every checklist item has a **machine-checkable acceptance command** — a `grep`, a named
     test, a parse check — no manual-only "looks right" items.
   - Canonical examples are **exact-equality assertions** (`assert out == ...`), never
     substring checks.
   - It names any **exact signatures** the implementer should copy, not invent (boto3 naming:
     `Bucket`, `Key`, PascalCase params).
   - It lists the **invariants from `architecture.md`** the phase must not break.
   - It follows the shape of `plan/phases/dacoburn-1-bucket-management-core.md` (Step 0
     baseline, checklist with acceptance commands, named tests, a **Files** list, Step Z
     close-out, an **Acceptance (verification session)** block).
4. Set the phase's row in the `light-s3-client.md` index to `planned — ready to implement`.
5. Log a one-paragraph entry in `ai-updates.md`: what phase you cut and its blast radius (grep
   the codebase + `plan/phases/` for every symbol the phase touches; list the hits).
6. `git add -A && git commit -m "plan <phase>: <slug>"`.

**Planner may NOT** set a phase to `awaiting verification` or `✅ complete`, and may not edit
`plan/defects.md` (that is the verifier's).

## Role 2 — IMPLEMENTER

**Reads only: this file, the ONE phase file, and `plan/architecture.md`. Nothing else to start.**

1. `git add -A && git commit -m "pre <phase>: baseline"`; paste `git log --oneline -1`.
2. Run `python -m pytest tests/test_unit.py -q` — record the baseline test count in
   `ai-updates.md` (your final count must exceed it). If `git status` shows dirty files you did
   not create, STOP and report — don't commit them.
3. Implement **only** this phase. Touch **only** the files in its **Files** list. No refactors
   beyond the task, no renames, no dependency changes unless the phase says so.
4. **Plan files are READ-ONLY except two edits:** flip `[ ]`→`[x]` (children before parents —
   never tick a parent over an unticked child) and set this phase's Status to
   `awaiting verification`. NEVER reword or delete a checklist item. `git diff -- plan/
   light-s3-client.md` is checked in verification; any other change fails the session.
5. **A checkbox is ticked only after running its acceptance command and pasting the real output
   into `ai-updates.md`.** A claim without reproducible pasted output counts as NOT DONE.
6. Append the session summary + all pasted outputs to `ai-updates.md` (newest on top).
7. `git add -A && git commit -m "<phase>: <one-line summary>"` — ONE commit per session so the
   verifier can diff exactly what you did. (Until phase dacoburn-15 lands: the legacy
   version-check pre-commit hook may bump `version.py` and abort the first attempt —
   `git add` the version files and commit again; that still counts as one work commit.
   After dacoburn-15: NEVER touch `version.py`/the `pyproject.toml` version — versions are
   owned by the release workflow and the PR freeze check will fail the session's PR.)
8. Set the phase Status (phase file + index row in `light-s3-client.md`) to
   `awaiting verification`. **You NEVER set `✅ complete`.** You never edit `plan/defects.md`.

## Role 3 — VERIFIER (adversarial — fresh context; a different model when available)

Your job is **to find where the implementer's claims are false.** Assume they are until you
have reproduced them. Owns `plan/defects.md` exclusively.

1. Fresh context. `git log --oneline` to find the implementer's baseline and work commits.
2. **Mechanical gate (all must pass):**
   - `python -m pytest tests/test_unit.py -q` green; final count exceeds the pasted baseline.
   - Run **every** acceptance command in the phase file yourself; compare byte-for-byte against
     the outputs pasted in `ai-updates.md`. A paste that could not have come from the shown
     command is **fabrication** and fails the session outright.
   - `git diff <baseline>..HEAD -- plan/ light-s3-client.md` shows ONLY checkbox flips + the
     Status line/row. Any reworded or removed checklist item fails the session.
   - `git status` clean of stray files; only the phase's Files list (+ `ai-updates.md`, plan
     files, `version.py`/`pyproject.toml` version bumps) changed.
3. **Adversarial analysis** — spot-check at least 3 ticked items at random against the code
   (including one sub-checkbox and one "test exists" claim), then attack the project's
   invariants (`architecture.md` → Invariants; `defects.md` → watch-list). A unit test that
   only passes because a mock deviates from real S3 behavior is a wrong test, not a pass. If a
   finding is genuinely uncertain, escalate it or flag it in `ai-updates.md` for a human —
   never wave it through.
4. **Verdict — you are the ONLY authority for ✅:**
   - All good → set the phase Status (file + index row) to `✅ complete (verified <date>)`.
   - Anything false → set Status to `⚠️ verification failed`, write the findings in
     `ai-updates.md`, and file each as a defect in `plan/defects.md` with the next D-number
     (severity, exact location, reproduction). The planner then cuts a remediation phase.
5. `git add -A && git commit -m "verify <phase>: <pass|fail>"`.

---

## Standing engineering rules (apply to every implementation phase)

1. **One phase per session. Never start the next.** Stop at a checkpoint if context runs low.
2. **Secrets from env only.** Never write a key/token/password into any file. Tests use mock
   credentials or the MinIO docker-compose defaults.
3. **Everything testable offline.** Unit tests mock `requests` — no live S3/MinIO required for
   `tests/test_unit.py`. Integration tests (`tests/test_integration.py`) may target the
   docker-compose MinIO but are never a phase's acceptance gate.
4. **All HTTP goes through `do_request`; all signing through `create_aws_signature`.** No
   direct `requests.*` calls and no hand-built `Authorization` headers in feature modules.
5. **New public `Client` methods follow the binding pattern** (see `architecture.md`):
   implemented in the right submodule, bound via `setattr` in `light_s3_client/__init__.py`,
   stubbed in the `TYPE_CHECKING` block, and documented in `README.md` + `ai-instructions.md`
   in the same phase.
6. **boto3-compatible naming.** Method names and parameters mirror boto3's S3 client
   (`Bucket`, `Key`, `Prefix`, PascalCase kwargs) unless the phase file says otherwise.
7. **Delete means delete** — no deprecated wrappers, commented-out code, or unused imports left
   behind. Check touched files for now-unused imports and zero-caller functions.
8. **Update `ai-updates.md` every session** (newest on top): date, role, phase, files touched,
   decisions, and the pasted outputs of every verification command you ran.
