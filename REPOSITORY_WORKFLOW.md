# Repository Workflow

**Related checklist task:** 0.3
**Project:** Android Password Manager

## Branches

- `main` is the stable submission branch.
- Each development task uses a short-lived task branch created from `main`.
- Branch naming format: `task/<checklist-id>-<short-description>`.
- Example: `task/0-3-repository-workflow`.
- A task branch should not be merged until its task is verified and the user has supplied the required `PASSKEY`.
- The agent must not rewrite published history or force-push.

## Commits

- Commits should contain one coherent change.
- Commit message format: `<checklist-id>: <imperative summary>`.
- Example: `0.3: define repository workflow`.
- Security-sensitive changes must identify the affected component in the commit body.
- Do not commit passwords, recovery keys, vault files, signing keys, `.env` files, or real user data.

## Issues and task tracking

- Each substantial task should have a corresponding GitHub issue when practical.
- Issue titles should begin with the checklist ID, for example `5.2 Implement Argon2id key derivation`.
- Issues should include scope, acceptance criteria, dependencies, and test evidence.
- The local `PROJECT_CHECKLIST.md` remains the authoritative task-status record.

## Pull requests

- Pull requests should identify the checklist task they implement.
- The description must summarize changes, tests, security impact, and known limitations.
- A pull request must not claim completion until the implementation is verified and the required user `PASSKEY` has been received.

## Releases

- `main` represents the latest stable project state.
- Release tags use the format `v0.<milestone>.<patch>`.
- The final capstone submission should use a clearly labeled release tag and include the tested APK or deployment instructions where permitted.
- Release notes must identify supported Android versions, test status, known limitations, and the prototype/security disclaimer.

## Required checks before merging

- Relevant automated tests pass.
- Manual verification is recorded when applicable.
- No secrets or real credentials are present.
- Documentation is updated.
- The local checklist reflects the actual task status.

