# R-01: password-entry visibility remediation

Prepared 2026-10-24. Execution authorized by the user's PASSKEY after the final
submission review. **Source fix approved and locally verified; the matching
APK is installed, with user-observed phone workflow results pending.**
The user's subsequent PASSKEY approved R-01 completion and merging PR #3.
R-02 subsequently built and installed matching version 0.1.1; see
[artifact/device identity and pending user results](r-02-android-update.md).

## Scope and behavior

NFR-USE-03 now has explicit Show/Hide controls for all six masked password
inputs, in addition to the existing saved-credential detail control:

| Screen | Field | Button while masked / revealed |
|---|---|---|
| Create your vault | Master | Show master password / Hide master password |
| Create your vault | Confirmation | Show confirmation / Hide confirmation |
| Welcome back | Master | Show master password / Hide master password |
| Create a new master password | New master | Show new master password / Hide new master password |
| Create a new master password | Confirmation | Show confirmation / Hide confirmation |
| Credential add/edit | Password | Show password / Hide password |

Each field starts masked and has an independent toggle. Confirmation visibility
does not change its paired master's visibility. Buttons use the existing
body/button typography, wrapping and scrolling behavior. A toggle changes only
Kivy's display-masking property; it does not change the string, authenticate,
write the vault, copy to the clipboard, or reveal the saved-detail view.
Existing copy authorization still requires explicit reveal on the detail screen.

Leaving a screen or clearing sensitive state resets masking and button labels.
Manual and automatic lock re-mask and clear even inactive screen inputs.
The credential-to-generator round trip preserves its draft, but re-masks the
field before leaving; applying or cancelling a generated password returns to a
masked entry. Successful setup re-masks its now-empty inputs before recovery-key
acknowledgement. Clicking a visibility control counts as activity while unlocked;
the inactivity threshold remains 120 seconds.

Recovery-key input and the generator's display were not redesigned. Crypto,
storage, password rules, clipboard behavior, Android secure-window flags,
dependencies and packaging configuration are unchanged. Showing a field does
not provide secure memory zeroization or repair the skipped keyboard-history issue.

## Local evidence

- Windows `.venv313`, Python 3.13.17, Kivy 2.3.1; in-memory synthetic test vaults
  and fake clipboard adapters, not personal data or the system clipboard.
- Latest full suite after the deterministic-clock correction: **132 passed in
  33.36 seconds**. This is the prior 107 cases plus
  25 new cases in `tests/test_password_field_visibility.py`, not 132 additional
  cases. Pip consistency and compileall passed.
- An initial full run also passed the same 132 cases in 32.34 seconds before a
  label-callback readability cleanup; a subsequent run passed in 36.27 seconds.
  The latest run above covers both that cleanup and the clock correction.
- The earlier targeted run was 25 passed in 7.65 seconds: an initial 20-case
  visibility set plus five existing UI regressions. It overlaps the full run.
- New cases cover all six independent toggles, unchanged text, labels/fonts,
  cleanup, navigation, both lock modes, generator apply/cancel, setup masking,
  activity timing, existing-entry editing and unchanged detail-copy authorization.
  Four small-viewport/enlarged-button cases check scrolling and wrapped heights.
- Four synthetic desktop previews were generated with the existing evidence
  harness in ignored `dist/r-01-previews/` and visually reviewed. They are not
  Android captures, are not packaged into an APK, and do not overwrite the
  approved mockup or historical task 9.7 screenshots.
- Remote CI results are recorded separately in the checklist/PR when available.
  Local success is not a substitute for physical Android rendering tests.
- A subsequent approval-commit CI run found one flaky exact-boundary timer
  test (131 passed, one failed). Its fake clock had been seeded from fractional
  real monotonic time. The test now uses explicit exact clock values to verify
  119 seconds remains unlocked and 120 locks, while retaining the production
  120-second setting. No application timeout or security behavior was changed.
  Rerun evidence is recorded in the checklist; the failed run is not a pass.

## Release boundary and phone follow-up

The published `v0.1.0` APK/tag and their checksum are unchanged. **Downloading
or reinstalling that same asset will not add this fix.** R-02 has built and
installed the separate 0.1.1 local test APK; user workflow results remain pending.
Do not replace an immutable
historical asset or move its tag to imply these changes were already tested.

When a matching new APK is available, record its source commit, filename/hash,
phone model and Android version, then verify using synthetic data:

1. Login, setup on a safe fresh test installation, new-master recovery, and
   credential add/edit each show the appropriate toggles, initially masked.
   Never uninstall or clear a needed vault just to test setup.
2. Each Show/Hide changes only its own field and label, preserving exact input.
3. Both generator apply/cancel preserve the draft appropriately and return masked.
4. Cancel/navigation and manual/two-minute lock re-mask on return; saved-detail
   reveal/copy still works under its original rules.
5. With the keyboard open and enlarged system text, scroll to all controls,
   submit valid input and confirm there is no new overlap or unreachable action.

Do not send passwords, recovery keys, vault files or sensitive screenshots as
evidence. These follow-ups do not waive other acceptance checks listed in the
[final review](../release/FINAL_SUBMISSION_REVIEW.md) and
[known limitations](../release/known-limitations.md).
