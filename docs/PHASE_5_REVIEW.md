# Phase 5 Review — Secure Vault Foundation

**Status:** Awaiting user approval  
**Review gate:** Gate 5  
**Review date:** October 22, 2026

## Review artifacts

- [Secure randomness](technical/secure-randomness.md)
- [Argon2id derivation](technical/argon2id-key-derivation.md)
- [Vault-key creation](technical/vault-key-creation.md)
- [Master-key wrapping](technical/master-key-wrapping.md)
- [Recovery-key wrapping](technical/recovery-key-wrapping.md)
- [AES-256-GCM encryption](technical/aes-gcm-encryption.md)
- [Encrypted SQLite storage](technical/encrypted-sqlite-storage.md)
- [Master-password setup and login](technical/master-password-setup-login.md)
- [Recovery reset](technical/recovery-reset.md)
- [Security-core tests](testing/security-core-tests.md)

## Phase 5 outcomes

- Random vault keys, salts, nonces, and recovery keys use the operating
  system-backed `secrets` CSPRNG.
- Argon2id derives 32-byte key-encryption keys with the approved baseline of
  64 MiB memory, 3 iterations, 1 lane, and 16-byte salts.
- The vault key is independent from both the master password and recovery key.
- Master and recovery wrappers use independent salts, fresh AES-GCM nonces,
  authenticated associated data, and distinct purposes.
- AES-256-GCM requires 32-byte keys, 12-byte nonces, non-empty associated data,
  and verifies authentication before returning plaintext.
- SQLite stores encrypted payloads and wrapper ciphertext rather than
  plaintext app names, usernames, or passwords.
- Setup, login, recovery reset, and session locking are implemented as local
  service operations.
- Security-core and integration tests pass: **44 tests passed**.

## Security review findings

The implementation uses established cryptographic libraries and rejects
weaker Argon2id parameters than the approved floor. Wrong passwords, recovery
keys, changed associated data, and tampered ciphertext produce generic
authentication failures.

The recovery design uses a high-entropy recovery key rather than storing
security-question answers. The recovery key is returned only as setup output;
the service does not persist it.

## Known limitations before production readiness

1. Argon2id performance has not yet been benchmarked on the target physical
   Android phone.
2. Android APK packaging and physical-device installation have not yet been
   validated.
3. Secure memory zeroization is not guaranteed for Python immutable byte
   objects.
4. Android platform protections, clipboard clearing, automatic inactivity
   locking, and screen-capture protections are not yet wired into the app.
5. The security services are not yet connected to the Kivy screens.
6. Database serialization and migration behavior require further release
   validation beyond the initial schema tests.

Therefore, the current implementation is a security-core foundation and not
yet a production-ready password manager.

## Gate 5 approval criteria

Gate 5 is approved when the user confirms that:

1. The secure vault architecture and key hierarchy are acceptable.
2. The recovery-key design is acceptable for phase one.
3. The cryptographic parameters and generic failure behavior are acceptable.
4. The 44-test result is sufficient to proceed to MVP functionality.
5. The listed limitations are understood and will remain release blockers until
   addressed or explicitly documented as final limitations.
6. The project may proceed to Phase 6, Task 6.1.

## Approval protocol

Reply with `PASSKEY` to approve Gate 5. The agent will then mark Gate 5 complete
and begin Phase 6, Task 6.1.
