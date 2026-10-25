# Lockbox test plan

Task 8.1. Prepared 2026-10-24 for review. Execution and final results are
separate tasks 8.2–8.8. This plan does not assert that unexecuted cases pass.

## Scope and environment

Verify the Python/Kivy Android MVP against `../requirements/mvp-acceptance-criteria.md`.
Cover authentication, recovery, encrypted storage, credential operations,
generation, clipboard, locking, Android protections, installation, and usability.
Biometrics, cloud sync, backup/export, and production certification are excluded.

Automated tests run in Windows Python 3.13 with `requirements-dev.txt` installed.
Android builds use the WSL Buildozer configuration and local recipes described
in `../release/installation-and-deployment.md`. Physical testing uses the project
phone; record its model, Android version, screen size, and system font setting.
The configured target is API 26+, ARM64/ARMv7; one phone does not establish
compatibility with every supported device.

Record source revision and dirty-tree status, Python/dependency versions, APK
SHA-256, build date, and release tag (`Lockbox_V0.1.0` for the published build).
Use synthetic data only, and do not include recovery keys or passwords in logs.
Use a disposable vault for destructive and tamper cases.

## Entry and exit criteria

Entry: build installs, app launches, test dependencies are available, and the
tested source can be identified. Preserve any needed vault before destructive
tests; without export support, use a separate test installation/device.

Exit: every mandatory acceptance criterion has evidence and a recorded result.
Security failures block acceptance. Other failures require a defect and fix
retest or explicit approved limitation. Missing evidence remains Not run or
Blocked. Checklist completion still requires user PASSKEY approval.

## Automated execution (task 8.2)

Run from the Windows repository root:

```powershell
.\.venv313\Scripts\python.exe -m compileall -q app main.py
.\.venv313\Scripts\python.exe -m pytest -q
```

Capture test counts, duration, exit code, and failures. Existing suites cover:

| Acceptance | Suites / review |
|---|---|
| AC-01,03,04 | `test_vault_service.py`, `test_ui_controller.py` |
| AC-05,06,07 | `test_randomness.py`, `test_recovery_reset.py`, `test_recovery_wrapping.py` |
| AC-08–12 | `test_credential_*.py`, `test_sqlite_storage.py` |
| AC-13,14 | `test_password_generator.py`, `test_password_strength.py` |
| AC-15,16 | `test_clipboard.py` plus physical timing |
| AC-17,18 | `test_session_controls.py` plus physical timing |
| AC-19 | `test_secure_window.py` plus physical capture test |
| SEC-AC-01–04,06 | `test_aead.py`, `test_kdf.py`, `test_wrapping.py`, `test_keys.py`, `test_security_integration.py`, storage/recovery suites |
| AC-02, SEC-AC-05 | Storage/log/repository inspection in addition to tests |

Historical result: 100 tests passed before the final typography changes;
syntax checks passed after those changes. Rerun against the final source in 8.2.

## Manual functional cases (task 8.3)

| Case | Procedure and expected result | Acceptance |
|---|---|---|
| M01 | Fresh setup: reject short/missing-category master passwords and confirmation mismatch; accept valid input | AC-01 |
| M02 | Confirm generated key is 16 ASCII alphanumeric characters; explicitly copy and paste into a temporary test field; compare exactly; verify secure-save confirmation before leaving setup | AC-05 |
| M03 | Wrong master password gives generic failure and no vault access; correct password unlocks | AC-03,04 |
| M04 | Add a synthetic entry; view masked password; reveal/hide; copy only the revealed password | AC-08,09,15 |
| M05 | Edit username/password, force-stop and relaunch, unlock and confirm persistence | AC-10 |
| M06 | Cancel deletion and retain entry; confirm deletion and verify absence after relaunch | AC-11 |
| M07 | Search matching, partial, mixed-case, and nonexistent names; verify correct results and empty state | AC-12 |
| M08 | Generate several passwords, check policy and strength feedback, use one in an entry | AC-13,14 |
| M09 | Copy password and time clearing at 30 seconds; repeat with recovery-key copy; copy other text before expiry and confirm it survives | AC-16 |
| M10 | Manually lock and verify reauthentication; idle for 120 seconds and verify lock; activity before expiry resets timer | AC-17,18 |
| M11 | Recovery with valid key resets master and preserves an existing entry; old master fails and new master succeeds; incorrect/case-changed new-format key fails without modification | AC-06,07 |
| M12 | Repeat setup/login and credential workflows in airplane mode | AC-21 |
| M13 (R-01) | On the matching rebuilt APK, test each setup/login/new-master/credential password-field Show/Hide independently; verify unchanged text, masked defaults, masking on navigation/manual/auto-lock and generator apply/cancel, and access with keyboard/enlarged fonts | NFR-USE-03; [R-01 detailed cases](password-field-visibility.md) |

User previously reported eight grouped workflow checks passed and confirmed the
revised app runs as expected. Preserve this as user-reported evidence, but do
not infer unreported negative, timing, persistence, or capture tests passed.

## Security cases (task 8.4)

- Inspect disposable SQLite data and application logs for synthetic plaintext
  credentials/master/recovery secrets (AC-02, SEC-AC-01,05). Do not publish raw
  secrets found in evidence. Scan tracked and proposed repository contents for
  vault files, credentials, signing keys, and secrets.
- Review Scrypt cost parameters, independent wrapper salts/purposes, AES-GCM
  nonce generation, and authenticated context against the architecture
  documents; run tampered ciphertext/tag and wrong-wrapper tests
  (SEC-AC-02–04,06).
- Attempt screenshots and screen recording on setup, recovery, and unlocked
  screens; sensitive content must be blocked (AC-19). Check behavior after
  background/resume and rotation attempts, and record any exposure.
- Inspect the final APK manifest for absence of Internet permission and test
  offline operation (AC-21). A previous APK manifest check is historical evidence.
- Verify legacy 52-character recovery keys still work on a disposable legacy
  vault after update. New keys are case-sensitive and have less entropy than
  the legacy format; do not describe them as 256-bit random keys.

## Usability and performance (task 8.5)

Verify text is legible and unclipped at final sizes: 21.6sp body/buttons/lists,
27sp headers, 16.2sp captions. Test small screens/system enlarged fonts where
available, keyboard visibility, long names, long generated passwords, scroll
access, captions, and errors. Record unavailable device configurations as untested.

Time visible usable startup (target <=5 seconds) and loaded search/navigation
(<=1 second). Create 100 synthetic entries and verify responsiveness and
operations (Q-AC-01–03). Record device and dataset conditions, observed times,
and repeated runs rather than substituting Android activity launch timing for
visible UI readiness.

## Installation and upgrade (task 8.6)

Follow the deployment guide for clean installation (AC-20, Q-AC-04), launch,
and initialization. Upgrade a disposable populated vault with `adb install -r`
using the same signing key; confirm entry persistence and login/recovery.
Verify the public release can download from another computer, compare SHA-256
with the tested APK, and install the downloaded copy. Public HTTP accessibility
was verified; full downloaded-file equivalence remains to be checked.

## Defects, results, and documentation (tasks 8.7–8.8)

For each defect record ID, severity, source/APK identity, environment, steps,
expected/actual behavior, and sanitized evidence. Fix and rerun affected cases
plus relevant regression tests; rerun the full suite for security/core changes.

Use this results template for each case/acceptance criterion:

| Case / criterion | Build / device | Date / tester | Expected | Actual / evidence | Status | Defect |
|---|---|---|---|---|---|---|
| Populate during execution | | | | | Not run | |

Allowed statuses: Pass, Fail, Not run, Blocked. Distinguish automated results,
agent inspection, and user-reported physical results. Final results must list
coverage gaps and approved limitations. Verify user/technical/deployment/test
documentation and known limitations at submission review (Q-AC-05).

Open acceptance concern: AC-05 requires explicit recovery-key save confirmation;
the reported happy-path test does not establish that this is enforced. Inspect
and test it before claiming acceptance, and record a defect if absent.
