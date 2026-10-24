# Installation and upgrade results

Task 8.6 was approved complete with the documented coverage gaps. See
[final results](final-test-results.md) for the consolidated cycle outcome.

Task 8.6. Device: user-reported Galaxy S25+, Android 17.

## Evidence and pending cases

| Case | Expected | Result |
|---|---|---|
| I01 Initial installation | APK installs and new vault can be initialized | Historical user-reported installation Success and setup Pass; exact initial clean-state verification and APK identity not captured |
| I02 Public artifact integrity | Downloaded release APK matches the tested build SHA-256 | Not run; public HTTP accessibility previously passed |
| I03 Data-preserving update | Installation with `-r` succeeds and existing master, recovery key, entries remain usable | User-reported Pass for reinstall, existing master login, and Upgrade Test entry preservation; post-reinstall recovery-key use not separately reported |
| I04 New-device clean installation | Install release on spare supported Android device without app data; initialize and use local vault | Not run; do not erase the primary phone to force this test |

The published build uses version 0.1.0. Reinstalling it over itself verifies
same-version replacement, not migration between different app/schema versions.
Report the version pair actually exercised. A signature mismatch is a failure
to investigate; do not uninstall a populated vault to bypass it.

## Execute with existing vault preserved

1. Add a disposable entry named `Upgrade Test` with dummy credentials; lock
   and unlock, and verify the entry before installation.
2. Download the APK from the published release into Windows Downloads. Use
   a fresh download and confirm its location; browsers may suffix repeated
   downloads with `(1)`.
3. Compare hashes if the original tested APK is still available in WSL:

```powershell
Get-FileHash -LiteralPath "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk" -Algorithm SHA256
Get-FileHash -LiteralPath '\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk' -Algorithm SHA256
```

If WSL now contains a newer build, different hashes may be expected; do not
claim the release is identical. Record the original uploaded artifact hash
instead if available.

4. Connect and authorize the phone, then run in PowerShell:

```powershell
adb devices
adb install -r "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk"
adb shell am force-stop com.xominnow.lockbox
adb shell am start -W -n com.xominnow.lockbox/org.kivy.android.PythonActivity
```

5. Verify existing master login, `Upgrade Test` entry and any other test entries
   persist. Test recovery with the previously saved key on a disposable vault,
   then verify entries still exist; never send the key in a report.
6. For I04, use a spare device with no existing Lockbox data if available.
   Otherwise report Not run. Initial-install history remains distinct from
   this specific release's clean-install test.

Record install output, data checks, checksum comparison, version pair, date,
and device. No uninstall or app-data-clear command is needed for I03.

Release: https://github.com/xominnow/password-manager/releases/tag/Lockbox_V0.1.0

## Execution outcome

The initial command was run in WSL with PowerShell syntax and returned no
devices; this was an execution-environment error, not an APK installation defect.
After receiving corrected Windows PowerShell instructions, the user reported
Pass for the reinstall/login/entry-preservation sequence. Raw successful install
output was not supplied. Treat this as same-version 0.1.0 replacement evidence.
Checksum comparison, fresh second-device installation, and post-reinstall
recovery remain coverage gaps, not passes. Await task-completion approval.
