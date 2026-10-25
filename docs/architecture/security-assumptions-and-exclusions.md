# Security Assumptions and Exclusions

**Project:** Android Password Manager
**Related checklist task:** 1.6
**Status:** Reconciled 2026-10-24; see [security decisions](security-decisions.md).

This document defines the conditions under which the phase-one design is expected to operate and the protections deliberately excluded from the capstone prototype.

## Security assumptions

| ID | Assumption | Design implication |
|---|---|---|
| SA-01 | The Android operating system and device firmware are not fully compromised. | The app relies on Android application sandboxing and platform security services. |
| SA-02 | The user selects a sufficiently strong master password and protects it. | Scrypt slows guessing but cannot make a weak password strong. |
| SA-03 | The user stores the recovery key securely and does not share it. | Loss of both credentials causes permanent vault inaccessibility. |
| SA-04 | Established cryptographic libraries and the approved random source function correctly. | The app does not implement custom encryption or random-number generation. |
| SA-05 | The device meets the supported Android baseline and has adequate storage. | Compatibility is validated on physical test hardware, not every Android model. |
| SA-06 | The user understands that the app is a capstone prototype and uses synthetic test credentials. | The project does not claim independent production security certification. |
| SA-07 | Source/docs are public and the approved debug APK is shared through GitHub Releases. | Real vaults, recovery keys, passwords, signing keys and local secrets remain outside Git and release attachments. |
| SA-08 | The app is operated offline in phase one. | No server, account system, cloud sync, remote recovery, or network threat model is required. |
| SA-09 | The user can access the physical device during normal use. | Phase one does not provide remote access or remote device recovery. |
| SA-10 | Android clipboard and secure-window behavior are available as documented by the platform. | Clipboard clearing and screenshot prevention may have device-specific limits. |

## Explicit exclusions

### Platform and operating-system exclusions

- Protection against a rooted or fully compromised device
- Protection against malware with accessibility, overlay, or screen-capture privileges
- Hardware forensic resistance
- Guaranteed secure memory wiping from Python-managed memory
- Protection against an external camera observing the screen

### Product-function exclusions

- Biometric unlock in phase one
- Cloud synchronization
- Multi-user accounts
- Browser extensions or autofill
- Cross-platform clients
- Hosted vault storage
- Administrator-assisted recovery
- Security-question recovery
- Remote password-breach monitoring
- Production account-recovery service

### Assurance exclusions

- Independent penetration testing
- Formal cryptographic verification
- Security certification
- Formal privacy/legal review
- Long-term vulnerability-response operations
- Guaranteed support for every Android phone

## Accepted residual risks

1. A weak or exposed master password may allow offline guessing despite Scrypt.
2. A lost recovery key cannot be reconstructed.
3. Clipboard contents may be observed by other apps and retained in keyboard
   history after active clipboard clearing; this observed fix was explicitly skipped.
4. Screenshot prevention does not stop external cameras or a compromised operating system.
5. Python and Android runtime behavior may retain sensitive values in memory longer than intended.
6. A public repository increases source visibility and requires disciplined secret handling.
7. A public debug APK does not provide the update, signing, or distribution assurances of a mature production product.
8. Device-specific Android behavior may affect timing, clipboard clearing, or secure-window enforcement.

## Release statement

The final project documentation must describe the application as a production-oriented capstone prototype. It must not state or imply that the application is independently audited, certified, or appropriate for storing real-world secrets.

## Review requirement

Any implementation decision that changes these assumptions or exclusions must update this document, the threat model, the non-functional requirements, and the known-limitations documentation.

Local tests and user-reported phone outcomes are recorded in the final report.
Unexecuted checks are coverage gaps, not automatically accepted requirement
waivers. Device KDF timing, complete artifact provenance and independent
assurance remain outstanding.

