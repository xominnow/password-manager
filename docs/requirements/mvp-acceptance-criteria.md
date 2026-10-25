# MVP Acceptance Criteria

**Project:** Android Password Manager
**Related checklist task:** 1.5
**Status:** Draft for review

The MVP is accepted only when all mandatory criteria pass and the evidence is recorded in the test results. Any exception must be documented as a known limitation and explicitly approved before submission.

## Functional acceptance criteria

| ID | Criterion | Required evidence |
|---|---|---|
| AC-01 | A new user can initialize a vault with a valid master password and confirmation. | Manual test record and initialization test. |
| AC-02 | The master password is not stored in plaintext in files, database records, logs, or repository contents. | Storage inspection, log inspection, and repository scan. |
| AC-03 | A returning user can unlock the vault with the correct master password. | Manual and automated authentication tests. |
| AC-04 | Incorrect master-password input leaves the vault locked and displays a generic failure message. | Negative authentication test. |
| AC-05 | Setup generates a high-entropy recovery key, displays it once, and requires confirmation. | Setup walkthrough and recovery-key test. |
| AC-06 | A valid recovery key permits the user to create a new master password without losing vault contents. | Recovery reset test with preexisting entries. |
| AC-07 | Invalid recovery-key input does not unlock or modify the vault. | Negative recovery test. |
| AC-08 | The user can add an app/website name, username, and password. | Add-entry test. |
| AC-09 | The user can view an entry with the password masked by default. | Manual UI test. |
| AC-10 | The user can edit an existing entry and observe the saved changes after relaunch. | Edit and persistence test. |
| AC-11 | The user can delete an entry only after explicit confirmation. | Delete and cancellation tests. |
| AC-12 | The user can search entries by app/website name without network access. | Search test in offline mode. |
| AC-13 | Generated passwords are at least eight characters and include uppercase, lowercase, number, and special-character classes. | Generator property test over multiple generated values. |
| AC-14 | The app displays understandable strength feedback for entered or generated passwords. | Strength-feedback test set. |
| AC-15 | The user can explicitly copy a password to the clipboard. | Manual clipboard test. |
| AC-16 | A copied password is cleared after 30 seconds when supported by the device. | Timed physical-device test. |
| AC-17 | The vault automatically locks after two minutes of inactivity. | Timed physical-device test. |
| AC-18 | The user can manually lock the vault and must authenticate again to reopen it. | Manual lock test. |
| AC-19 | Sensitive screens prevent screenshots and screen recording through Android secure-window behavior. | Physical-device capture test. |
| AC-20 | The app installs and runs on a physical Android device meeting the supported baseline. | APK installation record and screenshots. |
| AC-21 | Core functions operate without Internet access. | Offline test and manifest inspection. |

## Security acceptance criteria

| ID | Criterion | Required evidence |
|---|---|---|
| SEC-AC-01 | Vault records are encrypted and authenticated at rest. | Ciphertext inspection and tamper test. |
| SEC-AC-02 | Scrypt is used with documented parameters for master and recovery derivation. | Code review and configuration evidence. |
| SEC-AC-03 | AES-256-GCM uses fresh nonces for encryption and key wrapping. | Code review and nonce test. |
| SEC-AC-04 | The vault-encryption key is protected by separate master and recovery wrappers. | Storage-format inspection and recovery test. |
| SEC-AC-05 | No sensitive values are written to application logs or committed to GitHub. | Log inspection and repository secret scan. |
| SEC-AC-06 | Invalid ciphertext or authentication tags are rejected without exposing plaintext. | Tamper test and negative-path evidence. |

## Quality acceptance criteria

| ID | Criterion | Required evidence |
|---|---|---|
| Q-AC-01 | The app reaches a usable screen within five seconds on the selected test phone. | Timed startup result. |
| Q-AC-02 | Normal navigation and search respond within one second after data is loaded. | Manual timing result. |
| Q-AC-03 | The app remains usable with at least 100 test entries. | Data-volume test result. |
| Q-AC-04 | The project can be built from documented instructions. | Clean-build record. |
| Q-AC-05 | Required user, technical, deployment, testing, and limitation documentation is present. | Submission checklist review. |

## Entry criteria for MVP testing

- The approved UI flow is implemented.
- Security-critical modules have unit tests.
- The APK can be built and installed on the selected physical device.
- Test data is synthetic and clearly labeled.

## Exit criteria for MVP testing

- All mandatory criteria have a pass/fail result.
- Failed criteria have a documented defect or approved limitation.
- Security-critical failures are fixed or explicitly prevent release.
- Final test results are committed to the repository.

