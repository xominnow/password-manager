# Manual functional results

Historical task 8.3 record. Later fixes and their retests are consolidated in
[final results](final-test-results.md); initial failures below are preserved.

Task 8.3, started 2026-10-24. Test definitions are in `test-plan.md`.
Physical execution is performed by the user; the agent records reported
results and separately identifies source-inspection findings.

## Environment

User-reported physical phone: Samsung Galaxy S25+, Android 17.
Published release: `Lockbox_V0.1.0`. Exact installed APK checksum and its
equivalence to the local working source have not been verified.

## Prior physical evidence

The user reported Pass for all eight earlier grouped workflows: setup,
login, add entry, masking/reveal/copy/strength feedback, search/edit/delete,
manual lock/login, two-minute inactivity lock, and recovery. Following UI
and recovery-key refinements, the user stated the app runs as expected.
This is historical user-reported happy-path evidence; it does not establish
all detailed cases below passed.

## Detailed case record

| Case | Status | Evidence / checks still needed |
|---|---|---|
| M01 | Pass | User confirmed short/missing-category passwords and mismatched confirmation are rejected; valid setup previously passed |
| M02 | Fail | User confirmed 16-character alphanumeric recovery-key format and correct explicit copying; required save confirmation is absent in inspected source (DEF-01) |
| M03 | Pass | User confirmed wrong master rejected and correct master unlocks on Galaxy S25+, Android 17 |
| M04 | Pass | User reported add, masking, reveal/hide, and copy passed in earlier grouped workflow |
| M05 | Pass | User confirmed edited entry persists after closing/reopening the app; force-stop method not specified |
| M06 | Pass | User confirmed cancellation retains entry and confirmed deletion persists after reopening |
| M07 | Pass | User confirmed partial-name, mixed-capitalization, and nonexistent-name searches |
| M08 | Pass | User confirmed several generated passwords, strength feedback, and saving a generated password in an entry |
| M09 | Fail | User clarified password remains in keyboard clipboard history on Galaxy S25+, Android 17. Current-clipboard timeout, newer-text protection, and recovery-key clipboard timing still need separate results (DEF-02) |
| M10 | Pass | User confirmed activity resets the inactivity timer; earlier manual/two-minute locking checks passed |
| M11 | Pass | User confirmed incorrect recovery-key rejection, correct-key recovery preserving entries, and only the new master password unlocking; case-changed-key variant not separately reported |
| M12 | Pass | User confirmed fresh setup plus login, add, edit, and search in airplane mode |

Not run means the full detailed case has not been reported, even where part
of its behavior has historical evidence. Do not erase an existing vault to
perform these checks; use disposable test data for setup and deletion cases.

## DEF-01: setup omits recovery-key save confirmation

- Severity: medium; acceptance gap affecting recovery-key retention.
- Found by agent source inspection on 2026-10-24 in the current working tree,
  `SetupScreen` in `app/ui/screens.py`.
- Requirement: AC-05 requires confirmation that the recovery key is saved.
- Steps: create a vault; choose Back to login without confirming key retention.
- Expected: explicit save confirmation before normal setup navigation completes.
- Actual source behavior: Back to login navigates directly; no confirmation
  control or handler enforces this requirement.
- Status: open; physical reproduction pending. No fix applied during task 8.3.
- Retest after correction: leave setup before confirming, confirm retention,
  then verify login and recovery still work.

## DEF-02: physical clipboard check failed

- Severity: provisional high if a copied password remains accessible beyond
  the timeout; medium if clearing overwrites newer clipboard text.
- Environment: user-reported Samsung Galaxy S25+, Android 17.
- Test: copy a password with app open and check clearing after 30 seconds;
  separately copy other text before expiry and confirm it survives.
- Expected: app-owned password clears after timeout; newer clipboard text remains.
- Actual: user clarified the password remained in keyboard history. This does
  not establish whether the active clipboard timeout failed.
- Source finding: the adapter calls Kivy Clipboard.copy without explicitly
  attaching Android sensitive-content metadata in the application layer.
- Recommendation for defect-remediation task: mark Android password/recovery
  clips sensitive, test the actual keyboard behavior, and document that app
  clipboard clearing cannot guarantee removal of copies retained by keyboards.
  Sensitive metadata is a preview-protection signal, not guaranteed history erasure.
- Reference: https://developer.android.com/privacy-and-security/risks/secure-clipboard-handling
- Status: fix explicitly skipped by the user; retain keyboard-history retention
  as a known limitation. Active clipboard timing and newer-text protection
  remain unverified on device; do not report them as passed.
- Retest: password timeout and newer-text protection separately, then recovery-key
  copy timeout. Distinguish current clipboard contents from keyboard clipboard history.

## Execution conclusion

The requested manual testing cycle is finished and awaits task-completion
approval. Ten cases have user-reported Pass results; M02 and M09 retain Fail
results with the qualifications above. This is completion of test execution,
not a claim that all acceptance criteria pass. DEF-01 remains open for defect
remediation; DEF-02 remediation was skipped at the user's request. Outstanding
timing subchecks and the unreported case-changed-key variant remain coverage gaps.
