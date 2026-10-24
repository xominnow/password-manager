# Defect remediation and retest

Task 8.7. Changes apply to the current Windows working source. The published
GitHub APK is not updated by these edits. No vault data was erased.

| Finding | Implementation | Retest status |
|---|---|---|
| DEF-01 Missing recovery-save confirmation | Setup requires explicit `I saved my recovery key` action before normal navigation to login; master inputs clear after creation, recovery display clears after confirmation | Local UI regression passes; fresh-setup phone retest pending |
| DEF-02 Keyboard history | Fix skipped at user's request | Retained known limitation; clipboard behavior unchanged |
| DEF-03 Sensitive screen state | Screen-held fields/displays clear on navigation and on manual/automatic controller lock, including inactive screens. Recovery transfer and generator draft round trip remain usable | Local regression passes; user reports phone check 3 Pass. Fresh-setup cleanup still pending |
| DEF-04 Keyboard-open layout | Forms use one vertical scroll viewport; focus/viewport changes scroll focused field into view; inputs grow with text size. Initial resize setting replaced with SDL2-supported pan mode | User corrected initial Fail to Pass and subsequently reported keyboard-mode retest Pass |
| DEF-05 Enlarged-font layout | Labels/buttons wrap and grow with texture height; scrollable form and delete confirmation prevent fixed-height content overflow | Local enlarged-feedback test passes; user reports phone check 2 Pass |

Navigation regression: generator return now preserves draft app/username and
generated password, while clearing the generator's displayed value afterward.
Retaining a draft during the generator round trip is intentional; locking
clears it. Dropping Python/widget references is not guaranteed memory zeroization.

## Local verification

Project Python 3.13.17: compileall passed; full suite **107 passed in 26.25s**;
`git diff --check` passed. Five new real Kivy UI regression cases passed (manual
and automatic lock are separate parameterized cases). These are desktop UI
tests, not Android keyboard or vendor font-setting emulation.

Follow-up: user reports all three requested phone retests Pass, correcting the
initial keyboard Fail. During investigation the agent found Kivy's documented
SDL2 Android resize limitation and changed `Window.softinput_mode` to `pan`.
Source: https://kivy.org/doc/stable/api-kivy.core.window.html
After that change, compileall passed and all five UI regressions passed in
2.83 seconds. User subsequently reported Pass for the requested keyboard-mode
retest.
Fresh-setup confirmation still has local regression evidence only.

## Sync, build, install

In Ubuntu/WSL:

```bash
cd /home/xomin/password-manager
rsync -av \
  --exclude='.git/' --exclude='.venv*/' --exclude='.buildozer/' \
  --exclude='bin/' --exclude='__pycache__/' --exclude='.pytest_cache/' \
  "/mnt/c/Users/xomin/OneDrive/Documents/Fall I 2026/CIT Seminar/Password Manager/" \
  /home/xomin/password-manager/
source .venv-buildozer/bin/activate
buildozer android debug
```

After successful build, in Windows PowerShell:

```powershell
adb devices
adb install -r '\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk'
adb shell am force-stop com.xominnow.lockbox
adb shell am start -W -n com.xominnow.lockbox/org.kivy.android.PythonActivity
```

Do not reinstall the old GitHub download for this retest. Do not uninstall or
clear the existing vault. Preserve the same debug signing key for the update.

## Required phone retest

1. Open add/edit with keyboard visible. Scroll to all fields and Save/Cancel;
   save a dummy entry, then reopen and verify it.
2. Enlarge system font one step; verify all text/actions remain readable and
   reachable, including delete confirmation. Restore preferred font afterward.
3. Use the generator from a draft entry; app/username and chosen password
   survive return. Reveal a dummy credential, lock, unlock, and reopen it: it
   must be masked. Repeat with inactivity lock and verify recovery still works.
4. On a separate disposable fresh installation if available, create a vault:
   Back to login before save confirmation must be blocked. Save the key
   privately and select `I saved my recovery key`; login works and returning to
   setup does not expose the previous key. Do not erase the primary vault to
   perform this case; record pending if no fresh test installation is available.

Record Pass/Fail and observed behavior. Historical failures remain in prior
reports; fixes are pending device validation until these results are supplied.
