# Private APK distribution

Superseded for task 7.7: the user approved public GitHub Release distribution
with `PASSKEY`. See `github-release.md`. These private-sharing instructions
remain an optional alternative.

Related checklist task: 7.7. Distribute the tested debug APK privately to authorized testers. The public GitHub source repository is not the private download location.

## Prepare the download

After rebuilding and validating the APK, run these commands in Windows PowerShell. The timestamped folder avoids overwriting earlier packages. This copies the APK only, never a vault or recovery key.

```powershell
$apkSource = '\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk'
if (-not (Test-Path -LiteralPath $apkSource)) { throw 'APK not found. Confirm WSL is running and the build succeeded.' }
$packageDir = Join-Path ([Environment]::GetFolderPath('Desktop')) ('Lockbox-private-test-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $packageDir -ErrorAction Stop
$packageApk = Join-Path $packageDir 'lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk'
Copy-Item -LiteralPath $apkSource -Destination $packageApk -ErrorAction Stop
Get-FileHash -LiteralPath $packageApk -Algorithm SHA256
```

Record the SHA-256 value in the private message sent to testers. Upload the APK to a private OneDrive folder, choose sharing for specific people, and grant view/download access. Confirm the recipients and access settings before sending the link. Do not use an anonymous public link or a public GitHub release for this private test. No sharing link has been created by these instructions.

## Download on another computer

Sign in as an authorized recipient, download the APK, and compare its checksum against the sender's value:

```powershell
Get-FileHash -LiteralPath "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk" -Algorithm SHA256
```

Do not install if the values differ. Python, WSL, and Buildozer are not required on the recipient computer.

## Install on the phone

The supported target is Android 8.0/API 26 or newer with an ARM64 or ARMv7 processor. Device compatibility beyond the tested phone still requires validation.

Either transfer the APK to the phone and open it in the file manager, or use Android Platform-Tools on the recipient computer:

```powershell
adb devices
adb install -r "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk"
adb shell am start -W -n com.xominnow.lockbox/org.kivy.android.PythonActivity
```

For file-manager installation, allow installation from that source only if the phone requests it; revoke that permission after installation. Follow device security prompts. Managed devices may restrict private APK installation.

Each new installation has an independent local vault. Use synthetic test credentials, save the recovery key privately, and test setup/login, credential operations, copying, auto-lock, and recovery. Installation does not transfer another phone's vault. Updates require the same package identity and signing key to preserve existing data.

## Verification record

Before closing task 7.7, record the APK filename, build date, SHA-256, private access configuration, successful download by an authorized recipient, matching downloaded checksum, and installation outcome. Do not include the private sharing URL, real credentials, or recovery keys in the public repository.

This is a debug build for private evaluation; production signing and independent security review remain outside this distribution step. See `installation-and-deployment.md` for troubleshooting and destructive test-reset guidance.
