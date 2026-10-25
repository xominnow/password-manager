# Security-focused verification

Historical task 8.4 record. See [final results](final-test-results.md) for
subsequent remediation and the final disposition of the findings below.

Task 8.4, 2026-10-24. Agent local source review and automated execution;
physical Android results reported by the user. This is not an independent security audit.

## Automated evidence

Python 3.13.17, project `.venv313`, current modified local working tree.
Targeted command: `python -m pytest -q --basetemp <unique workspace cache directory>`
with `test_aead`, `test_kdf`, `test_wrapping`, `test_recovery_wrapping`,
`test_security_integration`, `test_security_verification`, `test_randomness`,
`test_session_controls`, `test_secure_window`, and `test_recovery_reset`.

Result: **43 passed in 11.83 seconds**, exit 0. Initial run had 42 passes and
one fixture setup error because pytest could not create its sandbox temporary
directory; rerun used a fresh directory under `.pytest_cache` and passed.

New verification checks establish that synthetic master/recovery secrets and
credential fields are absent from the closed test SQLite file and captured
Python logs/stdout/stderr for the exercised setup/login/create/view path.
They also exercise legacy 52-character Base32 recovery with an existing entry
and confirm entry recovery succeeds. These checks do not inspect Android logs,
live process memory, all failure paths, or the published APK.

## Source and repository review

| Control | Result and bounds |
|---|---|
| SEC-AC-01,06 | AES-256-GCM with authenticated context; tampered ciphertext/tag tests pass; disk synthetic-secret inspection passes |
| SEC-AC-02 | Scrypt n=65536, r=8, p=1, 16-byte salt, 32-byte output; minimum checks present |
| SEC-AC-03 | Random 12-byte AES-GCM nonces generated for encryption; no deterministic nonce scheme found |
| SEC-AC-04 | Independent salts and purpose-bound master/recovery wrappers reviewed; recovery tests pass |
| SEC-AC-05 | No sensitive-file extension candidates among tracked/proposed files; no matches for private-key headers, common GitHub token prefixes, or AWS access-key patterns in scanned non-environment/non-Git working files. App review found no explicit print/logging calls. This bounded scan is not full Git-history scanning or proof all secrets are absent |
| AC-19 | UI-thread FLAG_SECURE adapter tests pass; user reports screenshot capture and screen-recording session blocked on Galaxy S25+, Android 17 |
| AC-21 | Source configuration requests no Internet permission, app source contains no matching network imports in the performed search; historical manifest inspection passed. Current release manifest not re-extracted in this task |

Dependencies were not vulnerability-audited in this task. A passing local suite
does not prove the release APK contains the same code.

## Findings

- DEF-01 remains open: setup does not enforce recovery-key save confirmation.
- DEF-02: keyboard-history retention is a user-accepted skipped fix/known
  limitation. Do not infer that active-clipboard timeout passed on Android.
- DEF-03, medium, source-confirmed: sensitive screen state remains in widget
  properties after navigation or locking. For example, SetupScreen retains the
  recovery key and master input; NewMasterScreen retains its recovery key;
  EntryScreen and DetailScreen retain password text. Controller lock clears
  session/current view but does not clear these screen objects. This increases
  secret lifetime in memory and permits stale setup display/copy while the app
  process remains alive. Record for remediation with screen-state clearing and
  regressions; do not claim Python memory can be securely zeroized.
- The app defines no explicit on_pause/on_resume locking hooks; expiry checks
  run via the Kivy timer. The user confirmed login is required without vault
  exposure after backgrounding for over two minutes on the test phone. Other
  lifecycle timings and device configurations remain untested.

## Physical-device results

User-reported results on Galaxy S25+, Android 17:

1. Screenshot of revealed dummy password: **Pass — capture blocked**.
2. Screen recording: **Pass — recording session blocked**.
3. Background unlocked app for over two minutes and return: **Pass — user
   confirmed login required without exposed vault**.

Android log inspection and current-APK manifest inspection remain coverage gaps
unless separate sanitized evidence becomes available. Task stays open pending
completion approval; physical checks are finished. DEF-01 and DEF-03 remain
open for remediation; DEF-02 fix remains skipped at the user's request.
Execution completion does not mean all security findings have been resolved.
