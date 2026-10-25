# Lockbox technical documentation

Task 9.2. Implementation and maintenance reference, prepared 2026-10-24.
Describes the current working source, including phase 8 fixes. Source version
and installed/released APK identity must be recorded separately: changing this
checkout does not update GitHub release assets.

## Product and implementation boundary

Lockbox is a single-user, offline Android capstone prototype. Application logic
and UI are written in Python. Kivy, Android's runtime, OpenSSL, cryptography,
and other packaged dependencies include native components; Python application
code does not mean the APK contains only Python.

There is no backend, network account, synchronization, export/import, biometric
unlock, autofill, or browser extension. The app is not independently certified
for production password storage. See [test results](../testing/final-test-results.md)
for the bounds of verification.

## Source map and responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | Root Android launcher; delegates to the Kivy application |
| `app/main.py` | App creation, private user-data path, timer, Android secure-window startup, shutdown |
| `app/config.py` | Non-secret defaults for password policy and timers |
| `app/ui/navigation.py` | Route registration, initial setup/login route, lock cleanup callback |
| `app/ui/screens.py` | Setup/login/recovery, vault and entry screens, generation, responsive controls |
| `app/ui/controller.py` | Coordinates session, storage and application services for the UI |
| `app/security/randomness.py` | OS-backed random keys/nonces and recovery-key encoding |
| `app/security/kdf.py` | Scrypt derivation and parameter validation |
| `app/security/aead.py` | AES-GCM payload encryption/authentication |
| `app/security/keys.py` | In-memory vault-key object |
| `app/security/wrapping.py` | Purpose-separated master/recovery key wrappers |
| `app/security/vault_service.py` | Setup, unlock, recovery reset and master-password policy |
| `app/security/password_generator.py` | Secure generated passwords |
| `app/services/credentials.py` | Validation, serialization, encrypted CRUD and search |
| `app/services/password_strength.py` | Local heuristic strength feedback |
| `app/services/session.py` | Monotonic inactivity timer and manual lock |
| `app/storage/sqlite.py` | SQLite schema and transaction-backed persistence |
| `app/platform/clipboard.py` | Replaceable clipboard adapter and app-owned timeout tracking |
| `app/platform/secure_window.py` | Android UI-thread FLAG_SECURE operation |
| `p4a-recipes/` | Local native build recipes for cryptography and CFFI |

## Execution flow and service contracts

`PasswordManagerApp.build()` creates `VaultUiController` with
`Path(App.user_data_dir) / "vault.sqlite3"`. `build_app_shell()` creates all
screens and selects setup when no vault exists, otherwise login. Android
startup applies secure-window protection through the platform adapter.

`VaultUiController.setup(password)` initializes the database and returns the
recovery key to the setup screen. It does not unlock a session. The revised
setup screen requires `I saved my recovery key` before normal navigation to
login; this confirmation is UI state, not a persisted cryptographic factor.

`login(password)` and `reset_master_password(key, new_password)` establish an
`UnlockedVaultSession` and inactivity controller. Credential-service methods
require an unlocked session. `view(id)` selects an entry; `reveal_current()`
changes its display state; `copy_current_password()` additionally requires a
revealed password. `delete(id)` is called by the UI only after confirmation.

Credential read/authentication exceptions become generic UI status messages.
UI handlers catch broad exceptions, so diagnose a failure at the service boundary
using synthetic data; do not add logs that serialize user secrets.

## Cryptographic and format reference

| Item | Current implementation |
|---|---|
| Vault identifier | 16 random bytes, hex encoded in authenticated context |
| Vault data key | Independent random 32 bytes (256 bits) |
| Derivation | cryptography Scrypt; n=65536, r=8, p=1 minimums |
| KDF salt / output | 16 fresh random bytes per wrapper / 32 bytes |
| Master input | UTF-8, >=8 characters, uppercase/lowercase/digit/punctuation |
| New recovery key | 16 independent selections from ASCII letters/digits; case-sensitive, approximately 95 bits of random choice |
| Recovery compatibility | Strip spaces/hyphens; accept 16 ASCII alphanumeric bytes, or legacy Base32 decoded to 32 bytes |
| Encryption | cryptography AESGCM with 32-byte key |
| Nonce / authentication tag | Fresh random 12-byte nonce / 16-byte tag appended to ciphertext |
| Wrapper format | Version 1; separate master and recovery purposes |
| Record format | Version 1; deterministic JSON context and credential serialization |
| Database schema | Version 2 |

The legacy-named constant `RECOVERY_KEY_BYTES = 32` remains for legacy decoding;
new keys are not 256-bit random secrets. Do not uppercase new-format keys.

Setup creates one vault key and independently wraps it with master-derived and
recovery-derived keys using different salts and fresh nonces. Wrapper associated
data is canonical JSON containing `format_version`, `purpose`, and `vault_id`.
Record associated data contains `format_version`, `record_id`, `record_type`,
and `vault_id`. Serialization sorts keys and uses compact separators. Changes
to these contexts must be versioned: changing reconstruction breaks decryption.

Recovery authenticates the existing recovery wrapper, derives a new master
wrapper with new salt/nonce, and replaces only that wrapper in a transaction.
The vault key, encrypted records, and recovery wrapper remain unchanged.
Invalid authentication does not expose partial plaintext.

Password generation defaults to 20 characters, guarantees four character
categories, and uses `secrets` with a secure shuffle. The current UI has no
length selector. Strength scoring is heuristic, not a breach database lookup.

## Data persistence and compatibility

SQLite is not SQLCipher or whole-file encryption. App name, username and password
are canonical JSON encrypted together; salts, nonces, IDs, purposes, versions,
timestamps and algorithms remain visible metadata.

| Table | Stored data |
|---|---|
| `vault_metadata` | Single row with id=1, vault ID, format version and timestamps |
| `key_wrappers` | Master/recovery ciphertext, salts/KDF settings, nonces, version and timestamps; unique vault/purpose |
| `entries` | UUID-style hex entry ID, vault ID, record version, nonce, ciphertext and timestamps |
| `schema_migrations` | Schema-version ledger and application timestamp |

Foreign keys are enabled. Setup, updates, deletion and master-wrapper replacement
use transaction contexts and parameterized values. Names and usernames are
trimmed/required; credential passwords are required but are not forced to match
the master-password policy, allowing existing external credentials to be stored.

Search loads and decrypts all entries for the unlocked vault, then performs
case-insensitive substring matching on app names and sorts results. It is linear
in vault size and decrypts on each search; no plaintext search index exists.
Masked views still hold the actual password in memory.

Schema creation rejects a ledger newer than version 2. There is no complete
version-by-version migration engine merely because a migration table exists.
Changing table shapes or cryptographic formats needs explicit migration logic,
legacy fixtures and upgrade tests. SQLite deletion is logical deletion, not
guaranteed secure erasure of freed storage. No automatic backup/export exists.

## UI, sessions, and platform behavior

Post-release R-01 source adds `BaseScreen.add_password_input()` for all six
password inputs, each with an independent Show/Hide button. The toggle updates
only `TextInput.password`; the bound label stays synchronized, and a click
records qualifying activity without authenticating or copying. Shared cleanup
and pre-leave hooks reset masking, including the draft-preserving generator
path. Successful setup also resets masking before key acknowledgement. See
[R-01 tests and release boundary](../testing/password-field-visibility.md).
The published `v0.1.0` APK does not contain this later UI change.

Screens use a vertical ScrollView with content height derived from layout minima.
Labels and buttons wrap and grow from texture height; inputs grow with font size.
Keyboard focus/viewport changes schedule scrolling to the focused field. Kivy
uses `Window.softinput_mode = "pan"`; its SDL2 Android `resize` mode is unsupported.

Current text sizes use `sp`: 21.6 body/buttons/list items, 27 titles, and 16.2
captions. Portrait orientation is configured. Values are resolved at import;
live changes to Android font settings may require restarting the app.

A one-second Kivy timer checks clipboard expiry then inactivity. Inactivity uses
`time.monotonic()` with a 120-second threshold. Current activity updates come
from tracked input changes, navigation, authenticated controller actions and,
in the R-01 source, password-visibility clicks. Not every raw touch is tracked.
Manual/automatic lock drops the vault
key reference and current view, then invokes cleanup on all screens.

Screen transitions clear fields and secret displays. Entry-to-generator navigation
preserves an unsaved draft for the return trip; lock still clears it. Python
immutable strings and third-party/native buffers cannot be guaranteed zeroized.

Clipboard copies are explicit. The service remembers the copied value and time,
and after 30 seconds clears only if the current value still matches. The timer
depends on the app running; background/termination timing is not guaranteed.
The Kivy adapter does not explicitly set Android sensitive-content metadata.
Samsung keyboard history retained copied content; that fix was skipped by the
user. Neither password nor recovery clipboard history erasure is guaranteed.

Android `FLAG_SECURE` is applied using python-for-android `Runnable` on the UI
thread, with completion/error handling and a five-second wait limit. This avoids
the earlier SDL-thread window mutation crash. Initialization failures propagate.
Screenshot and recording blocking were user-tested. No explicit pause/resume
lock hooks exist; the tested >2-minute background return required login.

## Development and validation

From the repository root in Windows PowerShell:

```powershell
py -3.13 -m venv .venv313
.\.venv313\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv313\Scripts\python.exe -m app.main
```

For an existing environment, omit creation. Direct dependencies are
`Kivy==2.3.1`, `cryptography==50.0.2`; development adds `pytest==9.1.1`.
Transitive dependencies and the full Android toolchain are not comprehensively
locked by these manifests.

```powershell
.\.venv313\Scripts\python.exe -m compileall -q app main.py
$testTemp = Join-Path '.pytest_cache' ('run-' + [guid]::NewGuid().ToString('N'))
.\.venv313\Scripts\python.exe -m pytest -q --basetemp $testTemp
```

The full suite includes real Kivy desktop widget tests and requires an available
graphics/window environment, as well as service tests with platform fakes.
Latest full local run in task 9.9: 107 passed in 26.51s after the final pan-mode
adjustment; pip check and compileall passed. See the
[final report](../testing/final-test-results.md) for remaining test gaps.

The checked-in GitHub workflow installs dependencies, checks pip consistency,
compiles sources, and runs pytest on Ubuntu. It does not build/sign Android APKs
or execute physical tests. Xvfb and software rendering are configured for UI
tests; remote results are recorded separately in the
[snapshot evidence](../release/final-source-snapshot.md).

## Android builds and releases

Windows and WSL are separate source copies in this workflow. Sync before building;
otherwise a successful build may package stale code. Use the exact sync/build
commands in [deployment instructions](../release/installation-and-deployment.md)
or the [remediation rebuild guide](../testing/defect-remediation.md).

The WSL build environment uses Buildozer, Java 17, Rust/Cargo and Android SDK/NDK
tooling. `buildozer.spec` sets version 0.1.0, package `com.xominnow.lockbox`,
API minimum 26, ARM64/ARMv7 targets, and python-for-android `develop` revision
`0382d27`. No Internet permission is requested. Native code compilation and
toolchain downloads occur on the development machine.

Local cryptography/CFFI recipes force source builds instead of Android wheel
probing, use `--no-isolation`, and forward NDK API level/OpenSSL/libffi settings.
Cryptography uses Maturin/Rust; the CFFI recipe is version 2.0.0. Keep these
recipes with the build configuration when reproducing the APK. Buildozer/Cython,
host Python, Rust and SDK/NDK versions still need a final reproducible snapshot.

Build output is `bin/lockbox-0.1.0-arm64-v8a_armeabi-v7a-debug.apk`. Windows ADB
was used for physical installation; WSL USB access is not assumed. Same-signature
`adb install -r` preserves data; uninstall/clear-data deletes the vault. Preserve
the signing identity outside Git, and record the release APK SHA-256. Same-version
replacement passed; multi-version/schema migration has not been demonstrated.

Public GitHub Release distribution supersedes the original private-sharing plan.
The current APK is a debug build. Public release instructions are in
[github-release.md](../release/github-release.md). A release source commit,
APK checksum, dependencies and test evidence must refer to the same snapshot
before claiming reproducibility. Phase 9 release review remains pending.

## Maintenance and related references

Keep passwords, live vaults, recovery keys, debug/release signing keys and tokens
out of source, logs and test evidence. `.gitignore` reduces accidental inclusion
but does not remove already tracked secrets or establish a clean Git history.
Use disposable synthetic data when reproducing corruption/recovery failures.

For schema/crypto changes, add legacy and failure-path tests, preserve recovery
semantics, and retest on Android. For UI changes, rerun setup confirmation,
secret cleanup, generator draft, keyboard, enlarged-font and lock checks. A
passing desktop test cannot establish vendor keyboard or device behavior.

- [User manual](../user-manual/USER_MANUAL.md)
- [Architecture reference](../architecture/application-architecture.md)
- [Database schema](../database/schema.md)
- [Cryptographic parameters](../architecture/cryptographic-parameters.md)
- [Test plan](../testing/test-plan.md)
- [Final results and limits](../testing/final-test-results.md)
- [Known limitations](../release/known-limitations.md)

This guide is the consolidated current implementation reference. Earlier
task-specific technical notes preserve historical scope/counts where labeled;
architecture/database/security-decision reconciliation is handled by tasks
9.3 and 9.4, and final limitations/release review by later phase 9 tasks.
