# Recovery-Key Design

**Project:** Android Password Manager
**Related checklist task:** 1.4
**Status:** Updated to implemented recovery behavior, 2026-10-24; see [security decisions](security-decisions.md).

## Design decision

Phase one will use a high-entropy recovery key instead of security-question answers. The recovery key is intended to permit master-password replacement without exposing vault contents or storing a second low-entropy secret.

## Key hierarchy

The vault uses a randomly generated data-encryption key rather than encrypting all vault data directly with the user's password.

```text
Master password ──Scrypt──> Master key-encryption key ──AES-256-GCM──┐
                                                                         ├──> Vault encryption key
Recovery key ─────Scrypt──> Recovery key-encryption key ─AES-256-GCM───┘
                                                                                 │
                                                                                 └──> Encrypted vault records
```

## Setup flow

1. Select 16 characters independently using `secrets.choice` from ASCII letters and digits.
2. Display the case-sensitive alphanumeric key; canonical new-format input is 16 ASCII bytes. Legacy grouped Base32 input remains supported as 32 decoded bytes.
3. Generate a separate random 256-bit vault-encryption key.
4. Derive a master key-encryption key from the master password using Scrypt and a unique salt.
5. Derive a recovery key-encryption key from the recovery key using Scrypt and a separate unique salt.
6. Wrap the vault-encryption key once with the master key-encryption key.
7. Wrap the same vault-encryption key separately with the recovery key-encryption key.
8. Display the recovery key once in a secure screen.
9. Require the explicit `I saved my recovery key` acknowledgement before normal navigation to login. This is not re-entry verification or persisted proof of possession.
10. Store only the salts, KDF parameters, wrapped keys, nonces, authentication data, and version metadata.

## Storage requirements

The vault metadata must support two independent wrapped-key records with fields equivalent to:

- Format version
- Key purpose (`master` or `recovery`)
- KDF algorithm and parameters
- KDF salt
- Encryption algorithm and parameters
- Unique AES-GCM nonce
- Wrapped vault-encryption key and authentication tag

The recovery key itself must never be stored in plaintext. The master password must also never be stored in plaintext or as a reusable password hash.

## Normal unlock flow

1. The user enters the master password.
2. The app loads the master KDF parameters and salt.
3. The app derives the master key-encryption key.
4. The app attempts to unwrap the master-protected vault-encryption key.
5. The app rejects the session if authentication fails.
6. On success, the vault-encryption key is held only for the active session and is used to decrypt authenticated vault records.

## Recovery and password-reset flow

1. The user selects “Forgot master password.”
2. The app requests the recovery key.
3. Continue opens the new-master screen; this step does not validate the key.
4. The user enters/confirms a new master password and submits Reset password.
5. The service validates the new password, derives the recovery KEK with stored parameters, and authenticates the recovery wrapper.
6. Verification failure displays a generic message and does not modify the master wrapper.
7. The app derives a new master key-encryption key with a new salt.
8. The app creates a new master-protected wrapper for the existing vault-encryption key.
9. The previous master-protected wrapper is replaced or invalidated.
10. The recovery-protected wrapper remains available for future recovery.
11. The app opens a new authenticated session.

## Failure and loss behavior

- A lost recovery key cannot be reconstructed by the application.
- A forgotten master password and lost recovery key result in permanent vault inaccessibility.
- Invalid recovery input must not alter the vault.
- Interrupted reset operations must not leave the vault without a valid recovery-protected wrapper.
- Recovery-key entry must not be copied to the clipboard automatically.
- Recovery-key screens must use the same sensitive-screen protections as password screens.

## Security requirements

- Use distinct salts for master-password and recovery-key derivation.
- Use fresh random AES-GCM nonces for every wrapping operation.
- Bind wrapped-key ciphertext to its purpose and format version using authenticated associated data.
- Verify authentication before releasing or using the vault-encryption key.
- Never log passwords, recovery keys, derived keys, plaintext vault records, or ciphertext intended to remain private.
- Use generic authentication and recovery failure messages.
- Do not implement custom encryption or custom random-number generation.

## User-facing guidance

The setup screen must clearly state that the recovery key should be stored offline in a secure location. It must also state that the application cannot recover access if both the master password and recovery key are lost.

Current UI instructs the user to save the key; full loss guidance is in the
user manual. Explicit clipboard copying is permitted, never automatic, and
keyboard history may retain it (user-requested skipped fix). The requested
16-character format has about 95.3 bits of random choice versus the legacy
256-bit input. The key cannot restore deleted vault files. Confirmation state
is not persisted across process termination; save the key before leaving setup.

## Phase-one boundary

This design does not include biometric unlock, cloud recovery, account recovery by an administrator, or remote synchronization.

