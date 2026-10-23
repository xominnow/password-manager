# Scope Baseline and Acceptance Criteria

**Status:** Draft for review
**Related checklist task:** 0.1
**Deadline:** October 21, 2026

## Product definition

An Android-only, single-user, local-first password-manager prototype implemented with Python. The application is designed with production-oriented cryptographic practices but is not independently security-audited and must not be represented as suitable for storing real-world secrets.

## Approved assumptions

- Android is the only target platform.
- Application source code will be Python.
- Kivy is the proposed UI framework.
- APK packaging will use `python-for-android` and Buildozer.
- The supported baseline is Android 8.0/API 26 or newer.
- The vault operates locally and requests no Internet permission.
- The public GitHub repository contains source and documentation only.
- APK distribution is private for testing.
- Biometric unlock is deferred to phase two.
- The final deadline is October 21, 2026.

## Security baseline

- The master password is never stored.
- A one-time, high-entropy recovery key replaces security-question recovery.
- A random vault-encryption key is wrapped separately by the master-password key and recovery-key key.
- Argon2id is used for password-based key derivation.
- AES-256-GCM is used for authenticated encryption.
- Passwords are cleared from the clipboard after 30 seconds.
- The vault locks after two minutes of inactivity.
- Screenshots and screen recording are blocked while sensitive content is displayed.

## MVP acceptance criteria

The MVP is acceptable when:

1. A user can create a master password and initialize a vault.
2. A user can unlock the vault with the correct master password.
3. Incorrect passwords are rejected without revealing sensitive information.
4. A user can generate and save a recovery key during setup.
5. A user can reset the master password using the recovery key.
6. A user can add, view, edit, and delete an app/website name, username, and password.
7. Stored vault data is encrypted and authenticated at rest.
8. The password generator creates passwords of at least eight characters containing uppercase, lowercase, numbers, and special characters.
9. Password strength feedback is displayed.
10. A user can copy a password to the clipboard, and the clipboard is cleared after 30 seconds.
11. The application locks after two minutes without activity.
12. Sensitive screens prevent screenshots and screen recording.
13. The APK installs and runs on a physical Android device meeting the supported baseline.
14. The application does not require Internet access at runtime.
15. Automated and manual test results are recorded.
16. Required source code and project documentation are committed to the public GitHub repository.

## Explicit exclusions

- Biometric unlock in phase one
- Cloud synchronization
- Multi-user accounts
- Browser extensions
- Cross-platform clients
- Hosted password storage
- Production security certification or independent audit

## Review request

Review this baseline. If it accurately reflects the approved project, provide `PASSKEY`. The agent will then mark checklist task 0.1 complete and record the approval in the progress log.

