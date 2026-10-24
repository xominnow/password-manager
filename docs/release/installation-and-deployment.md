# Installation and deployment

Related checklist tasks: 7.6, 9.5. Updated 2026-10-24 for public test-APK
distribution. These are repeat-build instructions for the configured project
machine, plus end-user installation instructions. No server deployment is required.

## Download and install without a development environment

1. Open the [snapshot release](https://github.com/xominnow/password-manager/releases/tag/v0.1.0)
   and download the `.apk` under Assets. The source-code ZIP is not an installer.
2. Download on a phone directly, or transfer the APK from another computer.
3. Open it in the phone's file manager, follow the installation prompt, and
   allow installation from that source if requested. Revoke that permission
   afterward if desired.
4. Open Lockbox, create a vault, save the recovery key privately, and sign in.
   An existing vault requires its current master password instead of new setup.

[Direct APK download](https://github.com/xominnow/password-manager/releases/download/v0.1.0/lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk)

Python, WSL and Buildozer are not required by recipients. There is no desktop
vault client or automatic transfer of another device's vault. See the
[user manual](../user-manual/USER_MANUAL.md) for daily use and recovery.

The [task 9.9 snapshot record](final-source-snapshot.md) identifies the rebuilt
APK and source/package checks, separate from the historical `Lockbox_V0.1.0`
release. The snapshot APK still requires a fresh physical-phone smoke test.
Source edits do not update an existing release; compare the published checksum.

## Prerequisites

- Windows with Android Platform-Tools (`adb` available in PowerShell).
- WSL2 Ubuntu with the existing Buildozer environment at `/home/xomin/password-manager/.venv-buildozer` and Java 17.
- Android 8.0/API 26 or newer, ARM64 or ARMv7 phone, USB cable, and USB debugging enabled. Compatibility is configured for these targets; only the project test phone has been validated.
- Accept the phone's USB debugging authorization prompt. `adb devices` must show `device`.

These prerequisites are for maintainers using ADB/building, not normal APK users.
The existing WSL environment includes Rust/Cargo, C/C++ build tools, Python
packaging tools and downloaded Android SDK/NDK. Keep `main.py`, `buildozer.spec`
and both `p4a-recipes/` directories. See [build configuration](../technical/android-build-configuration.md)
for historical machine setup and [technical documentation](../technical/TECHNICAL_DOCUMENTATION.md)
for dependency choices. Exact host/toolchain versions are not fully locked;
an independent clean-machine reproduction remains unverified.

## Source and artifact record

Before a final build, record the source identity from the Windows project
directory in PowerShell:

```powershell
git rev-parse HEAD
git status --short
```

A dirty working tree means the commit hash alone does not identify the source.
Review and commit intended code/docs, including untracked files, before the
final source snapshot in task 9.9. Never include vaults, keys or real secrets.
No new commit, release upload or publication was performed by task 9.5.

## Sync and build

Run in Ubuntu/WSL, not Windows PowerShell. Windows is the source editing
location; WSL holds the separate build copy. Sync preserves WSL build caches
and its virtual environment. It copies changed files but does not remove old
files; review any obsolete packaged files when preparing a final source snapshot.

```bash
cd /home/xomin/password-manager
rsync -av \
  --exclude='.git/' \
  --exclude='.venv*/' \
  --exclude='.buildozer/' \
  --exclude='bin/' \
  --exclude='__pycache__/' \
  --exclude='.pytest_cache/' \
  "/mnt/c/Users/xomin/OneDrive/Documents/Fall I 2026/CIT Seminar/Password Manager/" \
  /home/xomin/password-manager/
source .venv-buildozer/bin/activate
buildozer android debug
```

Proceed only after the build succeeds and reports the generated APK. Expected output for the current version and architectures:

```text
/home/xomin/password-manager/bin/lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk
```

If version/architecture configuration changes, use the actual new output
filename consistently in installation commands and release notes. Do not
install a leftover APK after a failed build. Check its date and checksum.

For stale build output, run `buildozer android clean` before rebuilding. If clean reports a missing `python-for-android` directory, run the normal debug build to initialize the toolchain first. Keep `buildozer.spec` and `p4a-recipes/` together: they pin the Android dependency build configuration.

## Install or update

Run in Windows PowerShell with the phone connected and unlocked:

```powershell
adb devices
adb install -r "\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk"
adb shell am force-stop com.xominnow.lockbox
adb shell am start -W -n com.xominnow.lockbox/org.kivy.android.PythonActivity
```

Installation must report `Success`. The `-r` option preserves existing app data
when package and signing identity match. Preserve the build machine's debug
signing identity outside Git. On signature mismatch, obtain a build signed
with the original key; do not uninstall a populated vault to bypass the error.
Uninstalling deletes its data and recovery cannot reconstruct deleted records.

The launch command's `Status: ok` confirms Android accepted the launch; also visually confirm the app stays open.

For a GitHub-downloaded APK in Windows Downloads, use this installation command
instead of the WSL-path command (check for browser-added filename suffixes):

```powershell
adb install -r "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk"
```

Do not run PowerShell `$env:USERPROFILE` commands in Bash. A WSL ADB process
may report no devices even when Windows ADB can see the phone; USB passthrough
is separate from this documented Windows-ADB workflow.

## Verify artifact integrity

Compute SHA-256 on the actual built file in Windows PowerShell:

```powershell
Get-FileHash -LiteralPath '\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk' -Algorithm SHA256
```

After downloading the release, compute its checksum too:

```powershell
Get-FileHash -LiteralPath "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk" -Algorithm SHA256
```

Compare against the checksum of the artifact actually uploaded, not a later
local rebuild. Equal hashes establish identical bytes, not independent safety
or a match to source. Record actual values; no final SHA-256 is supplied here
because the current release/build equivalence has not been established.

## Device validation

Use dummy credentials. Verify setup, login, credential creation, masking/reveal,
copy, strength feedback, search, edit, deletion, manual/inactivity lock and
recovery. Current-source setup requires saved-key acknowledgement. New keys
are 16 case-sensitive alphanumeric characters; legacy keys remain valid and
are not shortened by an update. Clipboard clearing is best-effort and keyboard
history may retain copies; its fix was skipped. Do not claim guaranteed erasure.

Check text sizes and clipping on the phone: body/buttons/lists 21.6sp, headers 27sp, captions 16.2sp. Store the recovery key privately; never include it in submitted logs or screenshots.

For updates, create a dummy entry before installing; afterward confirm existing
master login and entry persistence. User-reported same-version replacement
passed, not a demonstrated different-version/schema migration. Test fresh
installation on a spare/disposable installation rather than erasing a needed
vault. See [installation results](../testing/installation-upgrade-results.md)
and [final report](../testing/final-test-results.md) for actual evidence/gaps.

## Troubleshooting

- `adb` not recognized: open a new PowerShell after adding Platform-Tools to PATH, or invoke its `adb.exe` by full path.
- Empty device list: check the USB cable, USB debugging, and Windows device driver.
- `unauthorized`: unlock the phone and accept its debugging prompt, then rerun `adb devices`.
- Verification failure: inspect the phone's installation/security prompt and applicable device restrictions before retrying.
- Changes absent: verify the Windows-to-WSL sync and successful rebuild before reinstalling.
- Signature mismatch: use the same signing identity; retain the populated app.
- Buttons hidden by keyboard: confirm the rebuilt scrolling/pan-mode version is installed, scroll the form or dismiss the keyboard, and retest with the actual system font setting.
- App closes: capture a fresh log while reproducing the launch:

```powershell
adb logcat -c
adb shell am start -W -n com.xominnow.lockbox/org.kivy.android.PythonActivity
adb logcat -d -v threadtime | Select-String -Pattern 'AndroidRuntime|FATAL EXCEPTION|python|kivy|Traceback' -Context 2,8
```

Review logs for sensitive content before sharing them.

## Optional destructive test reset

Only for a disposable test vault: the following command permanently deletes the app's local vault and settings. A recovery key cannot recover deleted vault data.

```powershell
adb shell pm clear com.xominnow.lockbox
```

Launch again to test fresh setup. Normal updates do not require this reset.

## Deployment boundary

This procedure produces a debug-signed test APK for public GitHub Release
distribution, not a production-signed or Play Store release. The original
private-sharing plan was superseded by user approval. Build/download tools need
Internet access; the installed app's vault workflows do not. APKs contain code,
not the developer's local vault. Each fresh installation creates an independent vault.

## Publishing and release record

Follow [GitHub release instructions](github-release.md). Record the actual
source commit and clean status, build date/tool versions, package/version,
APK SHA-256, signing identity reference (never the private key), release URL,
device tests and known limitations. Keep the tested APK unchanged between
checksum calculation and upload. Download and verify the published attachment.

For a future revision, use an appropriate reviewed version/tag rather than
pretending an older tag already includes new fixes. Task 9.5 changed instructions
only; the later build/tag/release operations are documented under
[task 9.9](final-source-snapshot.md). The original release remains preserved.
