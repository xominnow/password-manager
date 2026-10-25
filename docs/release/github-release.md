# GitHub APK release

## Final snapshot (task 9.9)

The new `v0.1.0` pre-release pairs the final source snapshot with the rebuilt
APK. See the [snapshot record](final-source-snapshot.md) for SHA-256, signing
identity, build inspection, source provenance and remaining phone-test gaps.

[Snapshot release](https://github.com/xominnow/password-manager/releases/tag/v0.1.0) ·
[Snapshot APK](https://github.com/xominnow/password-manager/releases/download/v0.1.0/lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk) ·
[Source ZIP](https://github.com/xominnow/password-manager/archive/refs/tags/v0.1.0.zip)

Publication/download results are recorded in the task progress log. The older
release below is historical and remains unchanged; do not use its checksum
for the rebuilt snapshot. Both builds retain app version 0.1.0, so compare
the asset hash/tag rather than relying only on the displayed version.

## Historical release

Tasks 7.7 and 9.5 use public GitHub Releases, authorized by the user with PASSKEY.
The user published release `Lockbox_V0.1.0`. On 2026-10-24, an unauthenticated
HTTP request followed the asset redirect and returned 200 OK with a content
length of 50,341,797 bytes. A complete download checksum comparison and
installation from another computer were not independently verified.

[Download APK](https://github.com/xominnow/password-manager/releases/download/Lockbox_V0.1.0/lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk)

[Published release](https://github.com/xominnow/password-manager/releases/tag/Lockbox_V0.1.0)

The following preparation instructions are for future releases. The recorded
release is already published, but its source/APK checksum equivalence is not
established. Task 9.5 updated documentation only; it did not change that asset.

1. Start Ubuntu/WSL and confirm the tested APK exists in
   `/home/xomin/password-manager/bin/`.
2. In Windows File Explorer, open
   `\\wsl$\Ubuntu\home\xomin\password-manager\bin`.
3. Open https://github.com/xominnow/password-manager/releases/new while signed
   in as a repository maintainer.
4. Review package version and select an unused release tag for the tested source
   commit. The existing tag is `Lockbox_V0.1.0`; do not assume a new local build
   is already attached to it. Final version/tag reconciliation is task 9.9.
   Review and commit intended source before recording its release identity.
5. Use a title that identifies the actual app version and test-build status,
   mark it as a pre-release, and adapt the notes below to the artifact tested.
6. Attach `lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk` using the release's
   binary attachment area. Do not add the APK to the source tree.
7. Calculate its SHA-256 in PowerShell and paste the value into the notes:

```powershell
Get-FileHash -LiteralPath '\\wsl$\Ubuntu\home\xomin\password-manager\bin\lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk' -Algorithm SHA256
```

8. Publish the release. Download the attached APK from another computer and
   verify its checksum, then install and launch it on a supported phone.
   Record the actual release URL and verification outcome in the checklist.

## Proposed release notes

This is a template, not a claim that these exact notes or a checksum are already
published. Complete the real checksum/version and disclose test gaps before use.

Lockbox is a local, single-user Android password-manager capstone prototype.
This debug APK is provided for testing and has not undergone an independent
production security audit. Use test credentials during evaluation.

Requires Android 8.0 or newer and an ARM64 or ARMv7 device. Compatibility has
been validated on the project test phone, not every Android device.

Features include an encrypted local vault, master-password login, recovery
key reset, credential creation/editing/deletion/search, password generation,
strength feedback, clipboard copying, and two-minute inactivity locking.

Download the APK under Assets, transfer it to your phone, open it, and approve
installation from the file source if prompted. Each new installation creates
its own local vault; vault synchronization and backup/export are not provided.
Save the recovery key privately. Deleting app data or uninstalling deletes
the local vault.

SHA-256: INSERT THE ACTUAL APK CHECKSUM BEFORE PUBLISHING.
