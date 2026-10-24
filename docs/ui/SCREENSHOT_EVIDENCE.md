# Screenshots and GUI mockup evidence

Task 9.7, prepared 2026-10-24.

## Approved custom mockups

[Original six-screen editable SVG](mockups/password-manager-mockups.svg)
is preserved unchanged. Checklist task 3.2 and Gate 3 record user approval.
It is a concept design, not an Android screenshot or pixel-identical final UI.

| Concept | Current implementation |
|---|---|
| Login, recovery, vault, credential, detail, generator | Retained as Kivy screens |
| Decorative phone frames, icons and status bar | Concept artwork, not claimed as implemented controls |
| Grouped recovery-key example / Verify key | New keys are 16 case-sensitive alphanumeric characters; Continue leads to new master entry; verification occurs on reset submission |
| Setup/recovery confirmation not pictured in original six frames | Current captures include setup and explicit saved-key acknowledgement |
| Compact typography and fixed concept layout | Current code uses larger sp sizes, dynamic wrapping and scrollable forms |
| Clipboard clears after 30 seconds | Best-effort active-clipboard clearing; keyboard history may retain copies |

## Current UI screenshot set

These are **staged desktop Kivy widget captures**, not Android-device images.
They use the real current screen classes with an in-memory database and dummy
values. They are interface illustrations, not proof of Android rendering,
keyboard behavior, secure-window enforcement, or published APK/source equivalence.

Environment: Windows, Python 3.13.17, Kivy 2.3.1, SDL2/OpenGL. Requested window
size 480x1040 desktop units; PNG exports are 600x1300 pixels at the observed
desktop scaling. A white presentation canvas is explicitly set by the evidence
harness. That does not establish the device's background, pixel scale, font
metrics, keyboard or system bars. No app layout/color source was changed for capture.

| Figure | Captured state | File |
|---|---|---|
| UI-01 | New-vault setup; copy/save acknowledgement disabled until creation | [Setup](screenshots/01-setup0001.png) |
| UI-02 | Staged saved-key acknowledgement state, using a public dummy key | [Recovery confirmation](screenshots/02-recovery-confirmation0001.png) |
| UI-03 | Existing-vault master login | [Login](screenshots/03-login0001.png) |
| UI-04 | Two synthetic vault entries and search | [Vault list](screenshots/04-vault0001.png) |
| UI-05 | Add/edit form with dummy values and strength feedback | [Credential form](screenshots/05-credential0001.png) |
| UI-06 | Credential details with password masked | [Credential details](screenshots/06-detail0001.png) |
| UI-07 | Generator with staged 20-character dummy value and demonstration feedback | [Generator](screenshots/07-generator0001.png) |
| UI-08 | Recovery-key input and Continue | [Recovery](screenshots/08-recovery0001.png) |
| UI-09 | Replacement master-password form | [New master](screenshots/09-new-master0001.png) |

The key shown in UI-02 is a public demonstration string, not the generated
recovery key protecting the temporary database. UI-07's value/feedback are also
staged fixtures. No real user vault, master password, recovery key or clipboard
contents were captured. The renderer uses an injected clipboard that refuses
copying. Full-widget rendering in a fresh process per screen avoids partial
desktop repaint/shared-texture export artifacts; images were then visually reviewed.

## Reproduce the captures

From the Windows project root in the configured graphical environment:

```powershell
.\.venv313\Scripts\python.exe -m scripts.capture_ui_evidence
```

To regenerate only the generator image:

```powershell
.\.venv313\Scripts\python.exe -m scripts.capture_ui_evidence --screen 7
```

The helper opens short-lived desktop windows and regenerates only the listed
PNG files from synthetic data. It does not alter a user vault or app source.
`scripts` is excluded from Android packaged source in `buildozer.spec`.

## Physical-device evidence

On the user-reported Galaxy S25+, Android 17, screenshot capture and screen
recording were blocked as intended. No bypass or weakened Android build was
introduced for this task. Physical results remain user-reported text evidence
in the [final test report](../testing/final-test-results.md).

No actual phone screenshots are included. If submission rules specifically
require device photographs, additional non-sensitive camera photos with dummy
data are needed; do not relabel these desktop captures as device photos.

## Submission use

Include the SVG, PNGs, this provenance/index, and the reproduction helper with
source documentation. Caption each image as a synthetic desktop UI capture or
concept mockup, as appropriate. Images do not waive missing acceptance checks
listed in the [known limitations](../release/known-limitations.md).
