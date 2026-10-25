# Final test results — capstone test cycle

Prepared 2026-10-24 for task 8.8. This report consolidates tasks 8.2–8.7;
it records completed execution, not unconditional acceptance of every requirement.

Task 9.9 supplement: the final local suite passed **107 tests in 26.51s** after
the pan-mode adjustment; dependency and compilation checks passed. The rebuilt
APK's SHA-256, signature, permission and 25-file bytecode/source checks are
recorded in the [source snapshot evidence](../release/final-source-snapshot.md).
Historical artifact gaps below describe the phase-eight cycle; this new APK
still needs a fresh physical-device smoke test. Earlier phone reports are not
retroactively attributed to the new hash.

## Environment and artifact identity

- Local automated tests: Windows, project `.venv313`, Python 3.13.17.
- Source: modified working tree based on commit
  `51f811db60cac0c10ae8653f978c323b8247c7dd`, including untracked files;
  the committed HEAD alone does not reproduce the tested source.
- Physical testing: user-reported Samsung Galaxy S25+, Android 17.
- Public release: [Lockbox_V0.1.0](https://github.com/xominnow/password-manager/releases/tag/Lockbox_V0.1.0),
  `lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk`.
- Public asset returned unauthenticated HTTP 200 with size 50,341,797 bytes.
  That check does not verify content integrity or source equivalence.
- No final source snapshot/APK SHA-256 pair has been recorded. Subsequent local
  fixes do not automatically update the public release. Physical results are
  user reports on their installed builds; the agent did not independently
  inspect each installed APK identity.

## Automated execution

| Stage | Result | Scope |
|---|---|---|
| 8.2 baseline | 100 passed in 23.48s | Full suite before new security/UI regression cases |
| 8.4 security | 43 passed in 11.83s | Targeted suite, including two new disk/log and legacy recovery tests |
| 8.7 regression | 107 passed in 26.25s | Full suite after confirmation, cleanup, scroll and wrapping changes |
| Final keyboard-mode adjustment | 5 passed in 2.83s | UI regressions after resize changed to pan; full suite not repeated afterward |
| Syntax and whitespace | Pass | Compileall passed after final code change; diff check passed during remediation |

These counts overlap; do not add them as distinct test cases. Total collected
cases at the last full run: 107. An initial security-run temporary-directory
fixture error was resolved by using a fresh workspace cache directory; the
rerun passed. There are no unresolved automated failures in the recorded runs.

## Physical-device outcomes

User reported successful setup/validation, correct and incorrect login,
credential creation/masking/reveal/copy, search variants, persistent edits,
delete/cancel behavior, password generation and feedback, manual locking,
inactivity timeout/reset, recovery preserving entries, and airplane-mode
operation. Recovery keys were reported as 16 alphanumeric characters with
working explicit copying.

Screenshots and screen recording were blocked. Returning after backgrounding
over two minutes required login without vault exposure. Reinstallation with
data preservation, existing master login, and the Upgrade Test entry passed.
This was same-version 0.1.0 replacement, not a schema migration test.

Readability, long text, and wording passed. Keyboard and enlarged-font cases
initially failed; user later reported all three remediation checks passed,
including the subsequent keyboard-mode retest. Startup was reported under
five seconds; exact measurements and repeat counts were not supplied.

## Defect disposition

| ID | Finding | Final disposition |
|---|---|---|
| DEF-01 | Recovery-key save confirmation missing | Implemented and local UI regression passed; fresh-setup physical retest not separately reported |
| DEF-02 | Copied password retained in keyboard history | Fix explicitly skipped by user; known limitation. Active-clipboard timeout and newer-text protection still lack separate phone results |
| DEF-03 | Sensitive text retained by inactive screen widgets | Cleanup implemented; manual/auto-lock local checks and user-reported phone check passed. No claim of secure Python memory zeroization |
| DEF-04 | Forms inaccessible with keyboard open | Scrolling/focus handling and pan mode implemented; user-reported retest passed after initial failure/correction |
| DEF-05 | Enlarged system font layout failure | Wrapping/dynamic sizing/scrolling implemented; local regression and user-reported phone retest passed |

Historical phase reports retain findings as they existed at discovery. This
report and `defect-remediation.md` give the subsequent disposition.

## Acceptance traceability

Pass means the cited checks passed within the stated environment; Partial means
the required evidence is incomplete. Local-only passes do not establish an
equivalent result on every Android device or the published APK.

| Criterion | Status | Evidence / outstanding qualification |
|---|---|---|
| AC-01 | Pass | User setup/password-validation checks and automated setup tests |
| AC-02 | Partial | Synthetic disk/column/log checks and bounded source/repository scan pass; Android logs/full Git history not inspected |
| AC-03,04 | Pass | Correct/wrong master local tests and user reports |
| AC-05 | Partial | Key format/copy pass; save confirmation fixed and locally tested, fresh-setup phone confirmation unreported |
| AC-06,07 | Pass | Recovery preserving entries and wrong-key rejection, local tests plus user reports; case-changed-key phone variant unreported |
| AC-08,09 | Pass | Credential creation and masked-by-default view tested/reported |
| AC-10 | Pass | Edit persisted after user closes/reopens app; exact force-stop method unspecified |
| AC-11 | Pass | Cancel retains entry; confirmed deletion persists after reopening |
| AC-12 | Pass | Search variants and airplane-mode search user-reported Pass |
| AC-13,14 | Pass | Generator/strength suites and user-reported use of generated passwords |
| AC-15 | Pass | Explicit password copying user-reported Pass |
| AC-16 | Partial | Local timeout/newer-value tests pass; device active-clipboard timing unverified. Keyboard-history retention is a known limitation |
| AC-17,18 | Pass | Manual lock, two-minute inactivity and reset behavior user-reported Pass |
| AC-19 | Pass | User reports capture/recording blocked; secure-window adapter regressions pass |
| AC-20 | Pass | Physical install and app usage reported; no sensitive screenshots collected |
| AC-21 | Partial | Offline flows Pass; source requests no Internet permission and historical manifest check passed, final release manifest not re-extracted |
| SEC-AC-01 | Pass locally | AES-GCM/storage tests and synthetic closed-database scan pass |
| SEC-AC-02 | Pass locally | Scrypt parameter validation/review/tests |
| SEC-AC-03 | Pass locally | Fresh random nonce generation reviewed/tested; no universal nonce-uniqueness proof |
| SEC-AC-04 | Pass locally | Independent master/recovery wrappers reviewed/tested |
| SEC-AC-05 | Partial | Captured local logs and bounded working-file secret scan pass; Android logs/full repository history/public source identity unverified |
| SEC-AC-06 | Pass locally | Invalid ciphertext/tag/context rejection tests |
| Q-AC-01 | Pass, user-reported | Startup <5 seconds; exact sample/repeats not recorded |
| Q-AC-02 | Not run | <=1-second loaded navigation/search timing unreported |
| Q-AC-03 | Not run | 100-entry device load test unexecuted |
| Q-AC-04 | Partial | Successful project builds/installations and instructions exist; independent clean rebuild from final committed snapshot not verified |
| Q-AC-05 | Pending phase 9 | Final manuals/technical docs/limitations and submission package review remain |

## Remaining limits and release conclusion

The tested prototype's core workflows are functional on the reported phone.
The test cycle does not establish production readiness or full acceptance:
several mandatory criteria still have partial or missing evidence, as listed
above. Only the clipboard-history fix was explicitly skipped; the other gaps
have not thereby been approved as requirement waivers.

Additional unverified areas include independent novice-user testing,
screen-reader support, smaller screens/other Android versions, new-device
release installation, downloaded APK checksum comparison, post-reinstall
recovery, dependency vulnerability auditing, and independent penetration testing.
Do not replace these with inferred passes or claim all Android phones tested.

No real credentials, recovery keys, vault files, signing keys, or private
download credentials belong in the submission evidence. The final source/APK
snapshot and documentation reconciliation belong to phase 9.

## Supporting records

- [Test plan](test-plan.md)
- [Baseline automated results](automated-test-results.md)
- [Manual functional results](manual-functional-results.md)
- [Security results](security-test-results.md)
- [Usability results](usability-test-results.md)
- [Installation/update results](installation-upgrade-results.md)
- [Remediation and device retests](defect-remediation.md)
- [Consolidated known limitations](../release/known-limitations.md)
