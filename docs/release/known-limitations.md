# Known limitations

Task 9.6, prepared 2026-10-24. Covers the current capstone source and recorded
tests, supplemented by the [task 9.9 artifact record](final-source-snapshot.md).
Earlier phone results do not establish behavior of the newly rebuilt APK.
Lockbox is a functional prototype, not an independently audited production
password manager. Use synthetic credentials during project evaluation.

## Observed issue: keyboard clipboard history (DEF-02)

The user reported that a copied password remained in keyboard history on the
Samsung Galaxy S25+, Android 17. The user explicitly requested skipping its
fix. This is a retained limitation, not a passed clipboard-erasure test.

The app attempts to clear a matching active clipboard value after 30 seconds
while its timer runs. It cannot guarantee removing copies retained by keyboards
or other apps. The adapter does not explicitly set Android sensitive-content
metadata, and expiry may be delayed while the app is suspended/stopped. The
same limits apply to copied recovery keys. Remove test secrets from keyboard
history manually; a copy/clear message does not prove all copies disappeared.
Active-clipboard timeout and newer-text protection pass local tests but lack
separate final phone results.

## Product and security constraints

| ID | Limitation | Effect |
|---|---|---|
| KL-01 | No backup/export/import or device transfer | Device loss, uninstall or app-data clearing can permanently remove records. A recovery key resets a master on an existing vault; it cannot reconstruct deleted data |
| KL-02 | No recovery-key re-display or rotation | Save the key privately at setup. The same key remains valid after master reset; lost master plus lost key means lost access |
| KL-03 | New recovery keys are 16 case-sensitive alphanumeric characters | About 95.3 bits of random choice, less than the legacy 256-bit input. A 32-byte derived key does not increase input entropy |
| KL-04 | Setup acknowledgement is transient UI state | Not proof by re-entry or persisted across process termination; save the key before leaving setup |
| KL-05 | Minimum master policy; no retry throttle/hardware-backed rate limit | Eight characters and four character categories do not guarantee a strong password; copied vaults permit offline guessing |
| KL-06 | No guaranteed memory zeroization | Cleanup drops references, but Python/native buffers may retain plaintext. Masking conceals display, not in-memory strings |
| KL-07 | Limited lifecycle/event tracking | No explicit pause/resume lock hooks; timers depend on app execution. Not every touch/scroll records activity. Background-return testing passed on one phone only |
| KL-08 | Visible metadata and in-memory search | IDs, counts, timestamps and crypto parameters remain visible. Search repeatedly scans/decrypts entries; it has no plaintext name index |
| KL-09 | No complete rollback/replay protection | GCM rejects invalid ciphertext/context, but valid older records or a whole older database can be replayed. Master reset does not revoke old database copies |
| KL-10 | Logical deletion, not physical erasure | SQLite row deletion does not guarantee removal of storage remnants or independent copies |
| KL-11 | KDF cost upper bounds incomplete | Minimum Scrypt costs are checked; malicious stored cost values can still cause excessive resource use |
| KL-12 | No complete numbered migration engine | A schema ledger and future-version rejection exist; arbitrary older schemas are not automatically upgraded by tested transformations |
| KL-13 | Trust in OS, dependencies and installer | Rooted/compromised-device, privileged-malware, external-camera and forensic resistance are not established; no independent supply-chain audit |

Documenting these constraints does not approve new requirements waivers. Only
the clipboard-history remediation was explicitly skipped.

## Features outside this MVP

- Biometrics: phase-two stretch goal; current unlock uses the master password.
- Cloud synchronization/hosted vaults, administrator recovery and remote device recovery.
- Multi-user accounts, multiple vault profiles and cross-platform clients.
- Browser extension, Android autofill and breach monitoring.
- Export/import, encrypted backups, device migration and automatic backup synchronization.
- User-facing generated-password length/category controls: current UI generates
  20 characters, although the underlying service accepts a length argument.

Editing a Lockbox entry does not update the external website's password.
Installing on another phone creates an independent vault, not a synchronized copy.

## Verification and acceptance gaps

| Area | Evidence | Still unverified |
|---|---|---|
| Compatibility | User-reported Galaxy S25+, Android 17; API 26+ ARM64/ARMv7 configured | Other models, Android versions and processors; every-phone compatibility |
| Recovery confirmation | Revised local UI regression passes | Explicit fresh-setup phone retest of acknowledgement flow |
| Performance | User-reported startup <5 seconds | Exact repeated timing, <=1-second search/navigation, 100-entry device load |
| Accessibility/usability | User-reported readable text, long names, wording and remediated keyboard/enlarged-font checks Pass | Independent novice users, screen readers, smaller screens and broader settings |
| Secrets/logs | Synthetic local disk/column/log checks and bounded working-file token scan pass | Complete Git-history scan and final Android application logs |
| Offline/permissions | Airplane workflows passed historically; task 9.9 rebuilt manifest requests no permissions | Fresh snapshot APK's offline phone retest |
| Installation/update | Initial install and same-version data-preserving reinstall user-reported Pass | Fresh release on another phone, different-version/schema migration, separate post-update recovery result |
| Artifact identity | Task 9.9 records rebuilt APK hash, signature and all 25 application bytecode/source matches | Publication verification is logged separately; independent clean rebuild and fresh snapshot phone smoke test |
| Automation/assurance | Final local suite 107 passed in 26.51s after final adjustment; CI configured with Xvfb/software graphics | Remote CI evidence is logged separately; independent security audit |

These are overlapping test runs, not 112 different cases. Missing evidence
does not become a pass because execution tasks were approved. Mandatory
criteria with partial/unexecuted evidence remain as recorded in the
[final report](../testing/final-test-results.md).

## Distribution and submission status

Public GitHub Release distribution superseded the original private-sharing
plan with user approval. The APK is a debug build, not a production-signed or
Play Store release. Source edits do not update published assets. Preserve the
package/signing identity for data-preserving updates; keep keys outside Git.
The toolchain and transitive dependencies are not fully locked.

Final source/tag/APK reconciliation is recorded in task 9.9. GUI evidence uses
synthetic desktop captures, not phone screenshots. Final submission review
remains a separate task. This document does not establish
uptime, ongoing maintenance, or a long-term vulnerability-response service.

## Remediated findings

DEF-01 save confirmation, DEF-03 stale screen values, DEF-04 keyboard layout
and DEF-05 enlarged-font layout were addressed in local source. Local tests
pass and requested phone retests were reported Pass, except the fresh-setup
confirmation coverage gap above. Do not describe the initial layout/state
findings as still unfixed, or assume every older APK has their fixes. See
[remediation evidence](../testing/defect-remediation.md).

## References and maintenance

- [Security decisions](../architecture/security-decisions.md)
- [Technical documentation](../technical/TECHNICAL_DOCUMENTATION.md)
- [User manual](../user-manual/USER_MANUAL.md)
- [Deployment guide](installation-and-deployment.md)
- [Final test results](../testing/final-test-results.md)

Revisit this register when controls, features, supported environments or
release artifacts change. Record evidence and user-approved exceptions
explicitly before changing a limitation's status.
