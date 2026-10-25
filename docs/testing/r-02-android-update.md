# R-02: Android visibility-fix build and phone verification

Task execution authorized by PASSKEY after R-01 source approval. Prepared
2026-10-24. **In progress — not a completed phone-acceptance result.**

## Build intent and identity

Build version `0.1.1` distinguishes this local test APK from published `v0.1.0`.
The package remains `com.xominnow.lockbox`; use the existing debug signing
identity for a data-preserving update. No database/crypto-format change,
uninstall, app-data clearing, release replacement or public publication is
included in this task. Existing GitHub tags/assets remain unchanged.

Application source comes from approved R-01 merge
`6821611cd33230c2d6a12c4c3135e7ca42cfec87`; the build-spec version change and
later evidence bookkeeping are tracked on `codex/r-02-android-visibility-build`.
Record the actual build commit, APK hash, manifest, certificate and installed
version after verification succeeds. Do not treat intended output as evidence.

## Before update (read-only checks)

- Windows ADB identifies one authorized project test phone, model `SM-S936U`.
- Device properties report Android `17`, API `37`.
- Installed app: version name `0.1.0`, version code `1026100`.
- Installed base APK SHA-256:
  `903c2074012f3fc29db8e4a48b4afa9c294f47f547d4b0f46a15afa4820d575f`.
- Installed APK signature verifies; public certificate SHA-256:
  `d0d43fb79f7e33508a3021d6dc821b056ed06b05d0041df55c20cdaf3c7bf5ee`.
- Only the installed code APK was copied to ignored local evidence output;
  no personal vault, master password, recovery key or private signing key was
  read/copied. The code APK is not a backup of vault data.

## Pending verification

- Successful WSL build and source/package comparison.
- APK version, permissions, signature and same-certificate check.
- Data-preserving `adb install -r`, installed version and stable launch checks.
- User-observed field toggle, navigation/lock, generator and keyboard/font results
  against the exact installed build, as outlined in
  [R-01 phone cases](password-field-visibility.md#release-boundary-and-phone-follow-up).
- Completion approval after actual results; other final-review acceptance gaps
  are not waived by installing this update.

Do not supply secrets as test evidence or delete an existing vault for a fresh
setup test. Use a safe spare test installation for setup/reset variants where
necessary. Android accepting a launch is not proof of visual correctness or a
five-second usable-screen benchmark.
