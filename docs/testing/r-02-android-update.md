# R-02: Android visibility-fix build and phone verification

Task execution authorized by PASSKEY after R-01 source approval. Prepared
2026-10-24. **Build/install verified; user-observed phone workflows pending.**

## Build intent and identity

Build version `0.1.1` distinguishes this local test APK from published `v0.1.0`.
The package remains `com.xominnow.lockbox`; use the existing debug signing
identity for a data-preserving update. No database/crypto-format change,
uninstall, app-data clearing, release replacement or public publication is
included in this task. Existing GitHub tags/assets remain unchanged.

Application source comes from approved R-01 merge
`6821611cd33230c2d6a12c4c3135e7ca42cfec87`; the build-spec version change and
later evidence bookkeeping are tracked on `codex/r-02-android-visibility-build`.
Build-input commit: `8cb1edcb43c0204b7ef1f28e4fc54b351aa69bc8` (committed
and pushed before source sync/build). Subsequent edits record results only;
they do not change the packaged application or version configuration.

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

## Verified build and artifact

| Field | Observed result |
|---|---|
| Output | `lockbox-0.1.1-arm64-v8a_armeabi-v7a-debug.apk` |
| Size | 50,345,621 bytes |
| SHA-256 | `f9c52f78552c927fd124f8e8feb0958e0b68f380e1ed5c6670de9b9146299ce9` |
| Package | `com.xominnow.lockbox` |
| Version name / code | `0.1.1` / `1026101` (greater than prior `1026100`) |
| Minimum / target SDK | 26 / 33 |
| ABIs | `arm64-v8a`, `armeabi-v7a` |
| Permissions | None requested; no Internet permission |
| Signature | Verification passed; Android debug certificate matches installed app |
| Certificate SHA-256 | `d0d43fb79f7e33508a3021d6dc821b056ed06b05d0041df55c20cdaf3c7bf5ee` |

The WSL Buildozer debug build succeeded using existing native caches. Windows
source and WSL app/launcher/config/recipes matched after ignoring CRLF versus
LF. All 25 packaged application bytecode files matched freshly compiled source;
none were missing/different. No docs, tests, scripts, Git, virtual environments
or build/output directories appeared in the private archive. No independent
clean-machine or byte-for-byte reproducibility claim is made.

The toolchain still emits nonfatal Gradle/deprecation and already-applied
cached Java-patch messages; a successful build is not an assertion that all
toolchain warnings were eliminated. Runtime/dependency configuration is unchanged.

Local copies (ignored output, not Git assets):

- WSL: `/home/xomin/password-manager/bin/lockbox-0.1.1-arm64-v8a_armeabi-v7a-debug.apk`
- Windows: `dist/r-02-build/lockbox-0.1.1-arm64-v8a_armeabi-v7a-debug.apk`
- [Checksum record](r-02-SHA256SUMS.txt) describes this local test build, not the
  public release's differently hashed 0.1.0 APK.

## Installation and bounded launch result

Windows ADB installed the verified local APK with `install -r`; result:
**Success**. No uninstall or app-data clear was run. Package inspection then
reported version `0.1.1` / `1026101`, with the original first-install timestamp
unchanged. On-device `sha256sum` of the installed base APK matched the build
hash above, establishing the exact installed artifact's identity.

Android accepted launch of `org.kivy.android.PythonActivity` with `Status: ok`
and reported `WaitTime: 3011` ms. The same app process remained running after
the subsequent check (at least 15 seconds later). Foreground/visual correctness
was not independently established; no phone screenshot/protection bypass was
used. The launch number is not a measured time to a usable screen.

This is a data-preserving update procedure, not independent confirmation that
the user's master login or each record survived. No vault contents were read.
Those functional observations must come from the user; package installation
success does not substitute for them.

## User-observed phone results still needed

| Case | Requested observation | Current status |
|---|---|---|
| P01 | Existing master login works and saved entries remain | Awaiting user |
| P02 | Login and credential add/edit Show/Hide independently toggle and preserve typed values | Awaiting user |
| P03 | Generator Use/Cancel returns a masked entry with appropriate draft preservation | Awaiting user |
| P04 | Navigation and manual/two-minute lock re-mask and require authentication as appropriate | Awaiting user; initial prompt asks manual lock, timed check remains separate unless reported |
| P05 | Keyboard-open/enlarged-font controls remain readable, scrollable and reachable | Awaiting user |
| P06 | Setup and new-master confirmation toggles on a safe fresh/recovery test flow | Not run on phone; do not erase a needed vault to test |

The user was asked for P01–P05 observations without sharing secrets. Detailed
safe follow-up cases are in [R-01 phone checks](password-field-visibility.md#release-boundary-and-phone-follow-up).
R-02 remains unchecked until results and a subsequent PASSKEY completion approval.
Unrun cases and broader final-review gaps do not become passes by implication.

## Reinstall this same test artifact if necessary

In Windows PowerShell, with the phone authorized:

```powershell
& 'C:\Android\platform-tools\adb.exe' install -r '\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.1-arm64-v8a_armeabi-v7a-debug.apk'
```

This installation was already performed; repeating it is not needed for the
current phone checks. Do not download the old GitHub APK expecting the fix.
No new GitHub Release or tag was created and no historical asset was replaced.

Do not supply secrets as test evidence or delete an existing vault for a fresh
setup test. Use a safe spare test installation for setup/reset variants where
necessary. Android accepting a launch is not proof of visual correctness or a
five-second usable-screen benchmark.
