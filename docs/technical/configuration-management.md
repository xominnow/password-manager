# Configuration Management

**Related checklist task:** 4.2  
**Status:** Draft for review

## Configuration policy

Application defaults are centralized in `app/config.py` through the immutable
`AppSettings` dataclass. The current defaults are:

- Product name: `Lockbox`
- Automatic lock timeout: 120 seconds of inactivity
- Minimum accepted password length: 8 characters
- Generated password length: 20 characters
- Generated password requirements: uppercase, lowercase, number, and special character

These values are product-policy defaults, not secrets. The master password,
security-question answers, recovery material, vault keys, and encrypted vault
contents must never be placed in source code, configuration files, or
environment variables.

## Dependency policy

- `requirements.txt` pins direct runtime dependencies.
- `requirements-dev.txt` pins the test dependency and includes runtime dependencies.
- Transitive dependency changes require rerunning import, test, security, and
  Android packaging checks.
- Local virtual environments and generated build artifacts are excluded by
  `.gitignore`.

## Future environment-specific settings

If development or test overrides become necessary, they must be explicit and
validated in a future configuration layer. Production defaults must remain
secure and the 120-second lock policy must not be silently weakened.
