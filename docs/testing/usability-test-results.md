# Usability verification

Historical task 8.5 record. See [final results](final-test-results.md) for
later successful keyboard/enlarged-font retests; initial failures are preserved.

Task 8.5, started 2026-10-24. Environment: user-reported Samsung Galaxy S25+,
Android 17. Current installed APK identity/checksum not independently verified.
Expected typography: body/buttons/lists 21.6sp, titles 27sp, captions 16.2sp.

This is a developer/user walkthrough, not a study with representative novice
participants. Earlier functional passes establish successful navigation through
core workflows, but not readability, accessibility, or response-time thresholds.

| Case | Procedure / expected result | Status |
|---|---|---|
| U01 | Read labels, titles, recovery-key text, strength feedback, and error messages on available screens. Text and controls remain visible, readable, and unclipped | Pass — user reported |
| U02 | Add/edit dummy entries with keyboard open; reach every field and Save/Cancel, dismiss keyboard and return without accidental data loss | Fail — user reported; DEF-04 |
| U03 | Use long app name `Example Demonstration Account With A Long Name` and username `long.test.username@example.invalid`; inspect list and detail, reveal/hide dummy password, and operate controls without obstructed actions | Pass — user reported |
| U04 | Temporarily enlarge Android system font one step, reopen app and repeat readability/input checks; restore original preference afterward. Record actual system setting and problems | Fail — user reported; DEF-05 |
| U05 | Confirm labels and validation messages make the next action understandable; note any confusing wording or navigation | Pass — user reported |
| P01 | Time launch to first usable screen (<=5s) and loaded navigation/search (<=1s), preferably three runs; record observed times and dataset size | Startup Pass — user reports <5s; exact time/repetitions/dataset unspecified. Search/navigation timing Not run |

Use dummy data; no new-vault reset is needed. Recovery text can be checked only
where available without deleting an existing vault; otherwise record that screen
as untested. Touch targets and readability depend on device configuration.

## Existing findings and coverage gaps

- DEF-01 recovery-save confirmation is absent, already recorded in manual results.
- Setup hints show an eight-character minimum, while validation messages do not
  always explain all four required character categories; evaluate whether the
  user can correct invalid input unaided (U05).
- Code uses fixed-height controls and labels; long text/enlarged-font results
  must be checked on device, not inferred from the font-size constants.
- Screen-reader behavior, smaller phones, other Android versions, and independent
  novice participants are not yet tested; do not claim full accessibility coverage.
- The planned 100-entry data-volume acceptance check remains unexecuted. Small
  dataset responsiveness does not establish that requirement.

## Results

User reported U01/U03/U05 Pass, U02/U04 Fail, and startup <5 seconds on the
project phone. Search/navigation timing and 100-entry load remain unreported.
Defects remain open until corrected/retested or accepted as documented
limitations. Task completion requires PASSKEY approval.

## DEF-04: keyboard-open form usability

- Severity: medium, provisional pending which actions are inaccessible.
- Reproduction: open add/edit form and show the keyboard on Galaxy S25+, Android 17.
- Expected: all fields and Save/Cancel remain reachable.
- Actual: user reports Fail; hidden controls/fields and exact screen pending clarification.
- Status: open; no code fix applied during usability testing.

## DEF-05: enlarged system font usability

- Severity: medium, provisional pending exact clipping/overlap.
- Reproduction: enlarge Android font one step and repeat readability/input checks.
- Expected: readable, unclipped content and reachable controls.
- Actual: user reports Fail; exact screen and system font setting pending clarification.
- Status: open; no code fix applied during usability testing. May share a layout
  cause with DEF-04, but not yet established.
