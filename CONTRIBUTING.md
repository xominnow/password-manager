# Contributing to Lockbox

Thank you for contributing to the capstone project. Keep changes small,
reviewable, and aligned with the approved requirements and checklist.

## Development workflow

1. Start from an up-to-date `main` branch.
2. Create a focused branch such as `feature/vault-storage` or `fix/login-validation`.
3. Make one logical change at a time.
4. Run `pytest -q` and the relevant syntax/import checks.
5. Update the appropriate technical documentation and known limitations.
6. Review `git diff` and `git status` before committing.
7. Use a descriptive commit message, for example `Add vault record model`.

## Security-sensitive changes

Changes involving passwords, recovery, cryptography, vault storage, clipboard
data, locking, Android permissions, or signing must include tests and a short
security rationale. Do not invent cryptographic primitives or store secrets in
source code, test fixtures, logs, or environment files.

## Code conventions

- Use Python-only application code for the approved Android stack.
- Prefer small functions with explicit inputs and outputs.
- Keep presentation, security, storage, and platform integration separated.
- Add or update tests with behavior changes.
- Document user-visible changes in the user manual or release documentation.

## Pull requests

A pull request should include:

- A concise summary of the change
- Tests run and their results
- Documentation updates
- Security or privacy impact, if applicable
- Known limitations or follow-up work

Do not include passwords, recovery answers, vault exports, private keys, or
other sensitive artifacts in pull requests.
