# Recovery-Key Design

**Project:** Android Password Manager
**Related checklist task:** 1.4
**Status:** Draft for review

## Design decision

Phase one will use a high-entropy recovery key instead of security-question answers. The recovery key is intended to permit master-password replacement without exposing vault contents or storing a second low-entropy secret.

## Key hierarchy

The vault uses a randomly generated data-encryption key rather than encrypting all vault data directly with the user's password.

```text
Master password ──Argon2id──> Master key-encryption key ──AES-256-GCM──┐
                                                                         ├──> Vault encryption key
Recovery key ─────Argon2id──> Recovery key-encryption key ─AES-256-GCM───┘
                                                                                 │
                                                                                 └──> Encrypted vault records
```

## Setup flow

1. Generate 32 random bytes using the platform-approved cryptographic random source.
2. Encode the bytes in a user-readable recovery-key format with grouping for transcription.
3. Generate a separate random 256-bit vault-encryption key.
4. Derive a master key-encryption key from the master password using Argon2id and a unique salt.
5. Derive a recovery key-encryption key from the recovery key using Argon2id and a separate unique salt.
6. Wrap the vault-encryption key once with the master key-encryption key.
7. Wrap the same vault-encryption key separately with the recovery key-encryption key.
8. Display the recovery key once in a secure screen.
9. Require the user to confirm possession by re-entering the recovery key or an equivalent full confirmation.
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
3. The app derives the recovery key-encryption key using the stored recovery KDF parameters.
4. The app attempts to unwrap the recovery-protected vault-encryption key.
5. If verification fails, the app displays a generic failure message and does not reveal which step failed.
6. If verification succeeds, the user creates and confirms a new master password.
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

## Phase-one boundary

This design does not include biometric unlock, cloud recovery, account recovery by an administrator, or remote synchronization.

