# Non-Functional Requirements

**Project:** Android Password Manager
**Related checklist task:** 1.2
**Status:** Approved baseline; final verification qualifications in the submission review

Final review R-01 found NFR-USE-03 partially implemented in `v0.1.0`.
The user authorized remediation: Show/Hide is now implemented for all six
password inputs in source and passes local regression tests, in addition to
saved-entry details. Completion approval and matching APK/phone verification
remain pending; see [R-01 evidence](../testing/password-field-visibility.md).
This is not a waiver or a claim that the published APK already has the fix.

## Security

| ID | Requirement | Verification |
|---|---|---|
| NFR-SEC-01 | The master password must never be stored in plaintext. | Code review and storage inspection. |
| NFR-SEC-02 | Vault credentials must be encrypted and authenticated at rest. | Security tests and encrypted-storage inspection. |
| NFR-SEC-03 | Password-based keys must be derived with the approved Scrypt configuration. | Code review and unit tests. |
| NFR-SEC-04 | Vault encryption must use AES-256-GCM with unique nonces. | Code review and encryption tests. |
| NFR-SEC-05 | Recovery must use the one-time high-entropy recovery key and must not use security-question answers. | Functional and code-review evidence. |
| NFR-SEC-06 | Incorrect authentication attempts must not reveal whether a specific credential or key component was valid. | Negative-path testing. |
| NFR-SEC-07 | Sensitive values must be masked by default in the interface. | Manual UI testing. |
| NFR-SEC-08 | Screenshots and screen recording must be blocked on sensitive screens. | Physical-device testing. |
| NFR-SEC-09 | The app must request no Internet permission and must not require network connectivity. | Manifest inspection and offline testing. |
| NFR-SEC-10 | Real credentials, live recovery keys, private signing keys and personal vault data must never be committed to GitHub. Public, clearly synthetic test fixtures and mockup examples are allowed. | Repository and secret scan; fixture provenance. |

## Session and privacy

| ID | Requirement | Verification |
|---|---|---|
| NFR-PRV-01 | The vault must automatically lock after two minutes of inactivity. | Timed physical-device test. |
| NFR-PRV-02 | A copied password must be cleared from the clipboard after 30 seconds when supported by the device. | Clipboard timing test. |
| NFR-PRV-03 | Manual lock must end the active vault session. | Manual functional test. |
| NFR-PRV-04 | The app must not collect analytics, telemetry, or remote account data in phase one. | Code and permission review. |

## Usability and accessibility

| ID | Requirement | Verification |
|---|---|---|
| NFR-USE-01 | A new user should be able to complete setup without technical assistance using the user manual. | Usability walkthrough. |
| NFR-USE-02 | Primary actions must use clear labels and consistent navigation. | UI review against approved mockups. |
| NFR-USE-03 | Password fields must provide a clear show/hide control. | Manual UI test. |
| NFR-USE-04 | Validation and error messages must explain corrective action without exposing sensitive data. | Negative-path UI tests. |
| NFR-USE-05 | Text and controls must remain legible on supported phone screen sizes. | Device compatibility review. |
| NFR-USE-06 | Destructive actions must require explicit confirmation. | Manual test. |

## Performance

| ID | Requirement | Verification |
|---|---|---|
| NFR-PERF-01 | The app should reach the first usable screen within five seconds on the test device after launch. | Timed physical-device test. |
| NFR-PERF-02 | Normal vault navigation and search should respond within one second after data is loaded. | Manual timing test. |
| NFR-PERF-03 | Authentication key derivation must use security-approved parameters; performance tuning must not weaken the security configuration. | Benchmark record and security review. |
| NFR-PERF-04 | The MVP should remain usable with at least 100 stored test entries. | Data-volume test. |

## Compatibility and deployment

| ID | Requirement | Verification |
|---|---|---|
| NFR-COMP-01 | The APK must target Android 8.0/API 26 or newer unless a documented compatibility constraint is approved. | Build configuration and device test. |
| NFR-COMP-02 | The app must install and run on the selected physical Android test phone. | Installation evidence. |
| NFR-COMP-03 | The APK must be buildable from documented Python project instructions. | Clean-build test. |
| NFR-COMP-04 | APK distribution may use the public GitHub Release approved by the user; vault storage remains local with no hosted password service. | Deployment review; public distribution supersedes the original private-sharing plan. |

## Reliability and data integrity

| ID | Requirement | Verification |
|---|---|---|
| NFR-REL-01 | Invalid or tampered vault data must be detected rather than silently accepted. | Tamper and authentication-tag tests. |
| NFR-REL-02 | An interrupted write must not silently replace valid vault data with partial plaintext or corrupt state. | Failure-path testing. |
| NFR-REL-03 | The app must provide a clear failure state when vault data cannot be decrypted. | Manual and automated negative tests. |
| NFR-REL-04 | The app must not log plaintext passwords, master passwords, recovery keys, or decrypted vault contents. | Log inspection. |

## Maintainability and testability

| ID | Requirement | Verification |
|---|---|---|
| NFR-MNT-01 | Security, storage, UI, and session logic must be separated into testable modules. | Architecture and code review. |
| NFR-MNT-02 | Dependencies must be pinned or version-constrained and documented. | Project configuration review. |
| NFR-MNT-03 | Automated tests must cover security-critical functions and core CRUD behavior. | Test report. |
| NFR-MNT-04 | Each release must identify supported Android versions, test status, and known limitations. | Release-note review. |
| NFR-MNT-05 | Documentation must remain synchronized with the checklist and implementation. | Final documentation review. |

## Capstone limitation

These requirements define a production-oriented prototype. Meeting them does not constitute independent security certification, penetration testing, formal verification, or approval for real-world password storage.

