# Threat Model and Trust Boundaries

**Project:** Android Password Manager
**Related checklist task:** 1.3
**Status:** Reconciled to implementation/accepted scope changes, 2026-10-24; see [security decisions](security-decisions.md).

## Security objective

Protect the confidentiality and integrity of locally stored credentials while the application is locked, in storage, and during normal authenticated use. The application is a local-only prototype and does not attempt to protect against a fully compromised Android operating system or a physically present attacker observing the user directly.

## Protected assets

| Asset | Sensitivity | Required protection |
|---|---|---|
| Master password | Critical | Never store; use only for key derivation. |
| Recovery key | Critical | Display once, never store in plaintext, and warn the user to protect it. |
| Vault-encryption key | Critical | Generate randomly and store only in wrapped form. |
| App/website names | Medium | Encrypt at rest with vault data. |
| Usernames | High | Encrypt at rest with vault data. |
| Passwords | Critical | Encrypt at rest and mask during display. |
| Clipboard contents | Critical | Explicit copy with best-effort 30-second active-clipboard expiry; keyboard history may retain copies. |
| Active session key material | Critical | Keep only while authenticated and clear on lock where practical. |
| KDF salts and parameters | Low/required metadata | Store with the vault; they are not secret but must not be modified silently. |
| Application source and build files | High for integrity | Protect repository history and exclude secrets. |

## Trust boundaries

### Boundary 1 — User and Android device

The user supplies the master password, recovery key, and vault data. The app trusts the Android OS to provide the application sandbox, secure display flags, and clipboard APIs. The app does not trust other applications to be harmless.

### Boundary 2 — Application UI and security core

UI code receives user input and requests operations from security and storage modules. Sensitive operations must remain in dedicated security modules rather than being implemented in UI event handlers.

### Boundary 3 — Security core and local storage

The storage layer may persist ciphertext, salts, nonces, authentication tags, and non-secret metadata. It must not persist plaintext credentials, master passwords, recovery keys, or active session keys.

### Boundary 4 — Application and Android clipboard

The clipboard is an external operating-system surface. A copied password may be visible to other apps depending on Android behavior, so copying must be explicit and time-limited.

### Boundary 5 — Application and public repository/build artifacts

The public repository is trusted for source integrity but is visible to everyone. It must never contain vault files, real credentials, recovery keys, signing keys, or local configuration secrets.

## Threat actors

- An attacker who obtains the phone while the app is locked
- A malicious or overly privileged application on the same phone
- A person who observes the screen or clipboard during use
- An attacker who obtains a copied vault file
- A contributor or automation process that accidentally publishes secrets
- An attacker who tampers with local vault data or application files
- An attacker who guesses or brute-forces a weak master password or recovery key

## Threats and controls

| ID | Threat | Mitigation | Residual risk |
|---|---|---|---|
| TM-01 | Vault file is copied from device storage. | Encrypt and authenticate vault data with AES-256-GCM; derive wrapping keys with Scrypt. | A weak user-selected master password remains vulnerable to offline guessing. |
| TM-02 | Attacker tampers with ciphertext or metadata. | Verify GCM tags/context and validate supported metadata. | Whole-vault rollback, valid ciphertext replay in the same context, deletion and all metadata changes are not universally detected. |
| TM-03 | Master password is exposed in storage or logs. | Never persist it; prohibit sensitive logging; inspect logs in testing. | Memory exposure on a compromised device is outside scope. |
| TM-04 | Recovery key is exposed during setup. | Display once, require confirmation, warn the user, and never write it to logs or files. | A person viewing the screen during setup could capture it. |
| TM-05 | Recovery key is guessed. | Generate 16 random case-sensitive alphanumeric characters; Scrypt; no security questions. | Approximately 95.3 bits of random choice, less than legacy 256-bit input; key exposure enables reset, key loss removes recovery. |
| TM-06 | Password is exposed through clipboard. | Explicit reveal/copy and best-effort active-clipboard timeout. | Samsung keyboard-history retention observed; fix explicitly skipped. Sensitive-clip metadata is not explicitly set; no history erasure guarantee. |
| TM-07 | Vault remains open when unattended. | Auto-lock after two minutes and provide manual lock. | The user may leave the app visible during the timeout. |
| TM-08 | Password is captured through screenshots or recording. | Enable Android secure-window behavior on sensitive screens. | External cameras and fully compromised devices are not prevented. |
| TM-09 | Public repository contains secrets. | Use `.gitignore`, test fixtures, secret scanning, and repository review. | A user may still intentionally or accidentally publish a secret. |
| TM-10 | Malicious app reads local files. | Use Android app-private storage and rely on OS sandboxing. | Rooted or compromised devices are outside the protection target. |
| TM-11 | Brute-force login attempts succeed. | Scrypt slows guessing; generic errors and app locking limit some exposure. | No implemented retry throttle or hardware-backed rate limit; weak master passwords remain guessable. |
| TM-12 | Dependency or APK is modified. | Pin dependencies, record build instructions, review releases, and document APK provenance. | No independent code-signing or supply-chain audit is included in the capstone. |
| TM-13 | Malicious database sets excessive KDF costs. | Minimum parameter checks and supported algorithm validation exist. | Comprehensive upper bounds are absent; resource-exhaustion protection is incomplete. |

Public APK distribution was approved through GitHub Releases. The app remains
offline, but build/distribution services and dependencies are supply-chain trust
boundaries. No final committed-source/APK checksum pair or full toolchain lock
has been verified; a local fix does not automatically update public assets.

## Out-of-scope threats

The following are explicitly outside the phase-one protection target:

- A fully compromised or rooted Android operating system
- Malware with accessibility or screen-capture control
- Hardware key extraction or forensic acquisition from a compromised device
- Phishing or social engineering of the user
- Recovery-key loss caused by user error
- Independent security certification or penetration testing
- Cloud-service compromise, because phase one has no cloud service

## Security acceptance conditions

The implementation may proceed only if the design preserves these conditions:

1. Plaintext master passwords and recovery keys are not stored or logged.
2. Vault records are authenticated as well as encrypted.
3. Key wrapping supports both normal login and recovery-key reset.
4. No network permission or remote service is required.
5. Residual risks remain documented in the final known-limitations report.

