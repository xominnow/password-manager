# Final source snapshot and APK identity

Task 9.9, prepared 2026-10-24. Release target: `v0.1.0`; application version
remains `0.1.0`. This is a capstone prototype/debug pre-release, not a
production-security certification. Task completion and merging require the
user's subsequent PASSKEY; task 9.10 final submission review remains separate.

## Source and release identity

- Repository: [password-manager](https://github.com/xominnow/password-manager).
- Review branch: `codex/9-9-final-source-snapshot`.
- New annotated tag: `v0.1.0`, created after source checks. Resolve its exact
  source commit with `git rev-parse 'v0.1.0^{commit}'`.
- [Snapshot release](https://github.com/xominnow/password-manager/releases/tag/v0.1.0)
  and [source ZIP](https://github.com/xominnow/password-manager/archive/refs/tags/v0.1.0.zip)
  are the publication targets. Publication/download verification is recorded
  in the task progress log after these operations succeed.
- Existing `Lockbox_V0.1.0` tag/release is preserved, not retagged or replaced.
  Its tag points to foundation commit `51f811db60cac0c10ae8653f978c323b8247c7dd`;
  it does not identify the later tested working tree.
- The source snapshot includes application code, tests, local packaging recipes,
  configuration, requirements, manuals, design and test evidence, UI mockups and
  synthetic screenshots. Virtual environments, caches, APKs, vaults and signing
  keys are not source files and are excluded.

## Rebuilt APK

| Field | Verified value |
|---|---|
| Asset name | `lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk` |
| File size | 50,344,953 bytes |
| SHA-256 | `8291242e02119d02fd2fafb674ef4608475c9820f572e5e017c600914ce385e6` |
| Android package | `com.xominnow.lockbox` |
| Version name / code | `0.1.0` / `1026100` |
| Minimum / target SDK | API 26 / API 33 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a` |
| Launch activity | `org.kivy.android.PythonActivity` |
| Requested permissions | None; no `android.permission.INTERNET` |
| Signing | Android debug certificate; APK signature verification passed |
| Certificate SHA-256 | `d0d43fb79f7e33508a3021d6dc821b056ed06b05d0041df55c20cdaf3c7bf5ee` |

[APK download target](https://github.com/xominnow/password-manager/releases/download/v0.1.0/lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk).
The accompanying [SHA256SUMS](SHA256SUMS.txt) identifies this APK only, not the
different historical release asset. The checksum is an integrity comparison,
not an independent guarantee that the app is secure.

## Build provenance and package inspection

Reviewed Windows source was synced to `/home/xomin/password-manager` in WSL
without overwriting its Git metadata, virtual environment or native caches.
The final build used the current `pan` keyboard mode and excluded the screenshot
helper directory. `buildozer android debug` completed successfully.

Observed tools: Ubuntu/WSL, Python 3.14.4, Buildozer 1.6.0, Cython 0.29.37,
OpenJDK 17, SDK build-tools 37.0.0, NDK r28c and python-for-android revision
`0382d27`. Runtime requirements: Python, Kivy 2.3.1 and cryptography 50.0.2;
local cryptography/CFFI recipes are included in the snapshot. Transitive and
host dependencies are not fully locked.

`aapt` confirmed package/version/SDK/ABI metadata and no requested permissions.
`apksigner verify --print-certs` passed. All 25 packaged application/launcher
bytecode files were compared with freshly compiled current source (matching
Python bytecode format); all matched, with no missing application files.
No `docs/`, `tests/`, `scripts/`, `.git/` or virtual-environment paths were found
in the packaged private archive. This cached-toolchain rebuild is not an
independent clean-machine or byte-for-byte reproducible-build demonstration.

## Verification and boundaries

- Windows Python 3.13.17: full pytest suite **107 passed in 26.51 seconds**,
  including the final keyboard adjustment; `pip check` and compileall passed.
- Bounded candidate-file scan found no matching private-key headers, token
  prefixes or risky vault/key file paths. This is not a full Git-history or
  independent security audit. Synthetic test credentials are deliberate fixtures.
- CI uses Ubuntu 24.04, Xvfb and software graphics for real Kivy widget tests.
  [GitHub run 40141573524](https://github.com/xominnow/password-manager/actions/runs/40141573524)
  completed successfully for source commit
  `096281a0b09e8d78c420df1a26295c44eff1d908` (dependency install/check,
  compilation and pytest). Subsequent release-record edits do not change the
  application code. Final-head CI evidence is logged in the task progress log.
- Earlier user-reported phone tests were on a Galaxy S25+, Android 17. The exact
  APK identity for each earlier report was not captured. This newly rebuilt APK
  has **not** received a new physical-device smoke test or fresh-setup check.
- Keyboard clipboard-history retention remains an observed issue whose fix the
  user explicitly skipped. Other acceptance gaps remain in
  [known limitations](known-limitations.md) and the
  [final test results](../testing/final-test-results.md).

Compare a downloaded APK in Windows PowerShell:

```powershell
Get-FileHash -LiteralPath "$env:USERPROFILE\Downloads\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk" -Algorithm SHA256
```

Do not uninstall or clear app data to update an existing vault. An update must
retain package and signing identity; preserve private signing material outside Git.
