# Security decision register

Task 9.4, prepared 2026-10-24. Records the implemented prototype's choices,
reasons, verification and residual risks. A decision recorded here does not
waive missing acceptance evidence; only explicit user decisions are exceptions.

## SD-01: local vault, public installer

Decision: one local vault per app installation; no backend, analytics, remote
account recovery or Internet permission. Public GitHub Release distribution was
explicitly approved with PASSKEY, superseding private APK distribution.

Reason: meet offline/single-user scope and allow installation from other computers.
Public source/installers do not mean publicly hosted user vaults. Trust Android's
app storage isolation, the installed APK and dependencies. A rooted/compromised
device is outside the tested protection target. No cloud or export backup exists;
deleted app data or lost devices can mean permanent data loss.

Evidence: source/build configuration, user-reported airplane-mode operation and
the [v0.1.0 snapshot record](../release/final-source-snapshot.md). Task 9.9
verified the rebuilt manifest/signature, all 25 application bytecode/source
matches, full public APK download checksum and all 157 tagged source ZIP files.
The rebuilt APK still needs a fresh physical-phone smoke test.

## SD-02: established cryptography, Scrypt key derivation

Decision: `cryptography` supplies Scrypt and AESGCM; Python `secrets` supplies
OS-backed random generation. No custom cipher, KDF or pseudorandom generator.
Scrypt uses n=65536, r=8, p=1 minimums, 16-byte salts and 32-byte output.

Reason: established library APIs, authenticated encryption, and an Android
packaging path without the additional Argon2 dependency. Earlier Argon2id-named
documentation filenames are historical; deployed source uses Scrypt.

Residual: derivation time has not been separately benchmarked on the phone.
Minimum validation exists; comprehensive upper bounds on untrusted KDF cost
parameters are not implemented, so a malicious database may cause resource
exhaustion. Dependency pins do not constitute a vulnerability/supply-chain audit.
The eight-character/four-category master policy is the approved functional floor,
not proof a particular master password resists offline guessing. There is no
implemented login retry throttle or hardware-backed rate limit.

Evidence: parameter validation, wrong-secret and encryption/tamper tests;
[security results](../testing/security-test-results.md).

## SD-03: independent data key and two authenticated wrappers

Decision: generate a random 256-bit vault key, wrap it separately under master-
and recovery-derived keys, and encrypt each credential record with the vault key.
Use independent wrapper salts, fresh random 96-bit nonces and 128-bit GCM tags.
Never deliberately reuse a nonce with a key; random generation is probabilistic,
not a globally enforced uniqueness database.

Reason: reset the master password without rewriting every encrypted record.
Deterministic JSON associated data binds wrappers to vault/purpose/version and
records to vault/ID/type/version. Authenticate before returning plaintext.

Residual: individual-record authentication does not prevent deletion, replay of
valid older ciphertext in the same context, or rollback of the entire vault.
An older database copy may still unlock with its older master password. The key
is not Android-Keystore-bound, and loss of both unlock secrets is unrecoverable.

Evidence: wrapper purpose/context, tamper and recovery-preserves-records tests;
[schema](../database/schema.md) documents exact versions/representation.

## SD-04: recovery key instead of security questions

Decision: random recovery keys replace the original two-security-question request.
The user later requested exactly 16 alphanumeric characters and explicit copying.
The current alphabet has 62 choices (A–Z, a–z, 0–9), selected independently;
16 * log2(62) is approximately 95.3 bits of random choice. New keys are
case-sensitive. This is shorter and lower entropy than the legacy 256-bit key;
Scrypt output length does not restore the lost entropy.

Reason: avoid guessable personal answers while meeting the revised usability
requirement. Legacy grouped Base32 keys remain accepted after decoding to
32 bytes. New keys canonicalize to 16 ASCII bytes after spaces/hyphens are removed.

The recovery key is not persisted in plaintext by the service. Setup displays
it, offers user-triggered copy, and requires `I saved my recovery key` before
normal navigation. That button is acknowledgement, not proof of possession via
re-entry; it is not a persistent setup lock surviving process termination.
Recovery verifies the key when the reset is submitted, replaces the master
wrapper, preserves entries, and keeps the same recovery key valid.

Residual: anyone possessing the recovery key and vault can reset the master.
There is no recovery-key rotation/re-display, server escrow or recovery of
deleted data. Save the key before leaving setup. Local confirmation regression
passes; a fresh-setup physical retest was not separately reported.

## SD-05: encrypt credential fields, expose required metadata

Decision: encrypt app name, username and password together before SQLite writes.
Keep IDs, versions, salts, nonces, algorithms and timestamps visible. Search
decrypts records inside the unlocked session and matches names in memory.

Reason: avoid a plaintext app-name index and support simple transactional storage.
This is application-level field/payload encryption, not SQLCipher or whole-file
encryption. Schema creation and vault initialization are separate operations.

Residual: row counts/timestamps reveal activity; search retains plaintext views
in memory and scans the vault. Logical deletion is not secure media erasure.
A schema ledger exists but a complete numbered migration engine does not.

Evidence: actual/documented SQLite DDL comparison, synthetic disk/column scans,
foreign-key/CRUD and tamper tests. Full Git-history and Android-log scans were
not performed; test fixtures intentionally contain dummy plaintext.

## SD-06: explicit copy with best-effort expiry

Decision: require an unlocked session and explicit reveal for password copying;
allow explicit setup recovery-key copying. Track the value and copy time in
memory; at 30 seconds clear only a matching current clipboard value.

Reason: make exposure deliberate and avoid overwriting newer user-copied text.
If another app copies identical text, the value comparison cannot distinguish it.
The running Kivy timer is required; background/process termination may interrupt it.

Observed exception: Samsung keyboard history retained a copied password. The
user explicitly requested skipping the fix. This remains a known limitation,
not a passed erasure test. The adapter does not explicitly set Android's
sensitive-content metadata; neither the password nor recovery-key history is
guaranteed removed. Active clipboard timeout/newer-text protection passed local
tests but lack separate phone results. Do not promise history-wide erasure or
infer that FLAG_SECURE protects clipboard content.

## SD-07: timeout, screen cleanup and limited lifecycle evidence

Decision: 120-second monotonic inactivity timeout and explicit manual lock.
Tracked text changes, navigation and authenticated actions record activity.
A one-second Kivy timer checks expiry; not every raw touch is recorded.
Lock invalidates the controller's session/key view and clears registered screens.
Entry/generator round trips preserve draft text only while the session is active.

Reason: constrain unattended access and reduce the lifetime of stale screen
values. Biometrics are deferred; master-password login is the primary unlock.

Residual: dropping references is not guaranteed memory zeroization. There are
no explicit pause/resume locking hooks. A >2-minute background return and
manual/inactivity locking passed on the test phone; that does not prove every
lifecycle timing or device safe. Persisted backup files retain their own secrets.

## SD-08: app-wide capture protection

Decision: Android FLAG_SECURE is enabled at startup through a python-for-android
UI-thread Runnable; window-operation failures propagate instead of reporting
success. The UI-thread fix addressed the observed SDL-thread startup crash.

Reason: block ordinary Android screenshots/recording of sensitive app content.
User reports confirm screenshots and recording were blocked on Galaxy S25+,
Android 17. Desktop adapter fakes do not prove Android behavior elsewhere.
External cameras, privileged malware and a compromised OS remain out of scope.

## SD-09: prototype distribution and provenance

Decision: distribute the debug APK as an explicitly identified public test build,
keep signing keys and vault data out of Git, and preserve signing identity for
data-preserving updates. Source code and documentation are intended to be public.

Residual: full toolchain/transitive dependency locking, final committed source
snapshot/APK hash equivalence, verified current CI, production signing and
independent audit are unfinished. Debug build success and 107 passing local
tests do not establish production security. Publication after local fixes is
a separate build/upload action, not an automatic effect of editing the repo.

## Evidence and remaining decisions

The [final results](../testing/final-test-results.md) distinguish local tests,
user-reported phone outcomes, partial acceptance and unexecuted checks. Missing
performance, accessibility, release identity and fresh-device evidence are not
silently waived by approving this document. The clipboard fix is the explicit
skipped remediation; remaining gaps stay recorded for submission review.

Changing KDF/nonce/context formats, key lifecycle, recovery, clipboard handling,
network scope or release signing requires updated threat assumptions, compatible
data handling and targeted regression/device evidence.
