# Vault-Key Architecture

**Project:** Android Password Manager
**Related checklist task:** 2.3
**Status:** Draft for review

## Design objective

Separate the key that encrypts vault records from the user's authentication secrets. This permits master-password reset through the recovery key without decrypting and re-encrypting every vault record.

## Key hierarchy

```text
Master password
       │ Argon2id + master salt
       ▼
Master key-encryption key (KEK-M)
       │ AES-256-GCM wrapper
       ▼
                         ┌────────────────────────┐
Recovery key             │ Vault-encryption key   │
       │ Argon2id +       │ (random 256-bit DEK)   │
       │ recovery salt    └───────────┬────────────┘
       ▼                              │ AES-256-GCM
Recovery key-encryption key (KEK-R)   ▼
                              Encrypted vault records
```

## Key material

### Vault-encryption key

- Generated randomly during vault initialization.
- 256 bits in length.
- Used only for authenticated encryption of vault records.
- Never derived from the master password or recovery key.
- Held in memory only during an unlocked session where practical.

### Master key-encryption key

- Derived from the user-entered master password using Argon2id.
- Uses a unique random salt stored as non-secret vault metadata.
- Output is used only to protect the vault-encryption key.
- A new master password receives a new salt and a new derived KEK.

### Recovery key-encryption key

- Derived from the one-time high-entropy recovery key using Argon2id.
- Uses a unique salt separate from the master-password salt.
- Output is used only to protect the vault-encryption key.
- Remains available after a master-password reset unless the recovery design is intentionally rotated in a future version.

## Wrapped-key records

The vault metadata stores two independent wrappers for the same vault-encryption key:

```text
wrapper_id
purpose                # master or recovery
format_version
kdf_algorithm
kdf_parameters
kdf_salt
encryption_algorithm   # AES-256-GCM
nonce
wrapped_key_ciphertext # includes or is stored with the authentication tag
associated_data_format
```

The wrapper's authenticated associated data must bind at least the format version, wrapper purpose, and vault identifier. A wrapper intended for recovery must not be accepted as a master wrapper merely because decryption succeeds.

## Vault-record encryption

Each stored credential record is encrypted with the vault-encryption key using AES-256-GCM.

The encrypted record should include:

- Record identifier
- Format version
- Random nonce
- Ciphertext
- Authentication tag, either appended by the library or stored separately
- Non-secret record metadata required for lookup, if any

The app/website name should be treated as sensitive by default and encrypted with the username and password. Search may decrypt records only inside an authenticated session.

The associated data should bind the record identifier, record type, and format version so that authenticated ciphertext cannot be silently moved between records or interpreted under the wrong schema.

## Lifecycle operations

### Initialization

1. Generate the vault-encryption key.
2. Derive KEK-M and KEK-R.
3. Wrap the vault-encryption key independently under each KEK.
4. Persist only wrappers and non-secret parameters.

### Normal unlock

1. Derive KEK-M from the entered master password.
2. Authenticate and unwrap the vault-encryption key.
3. Reject the session on any authentication failure.
4. Decrypt records only while the session is unlocked.

### Recovery reset

1. Derive KEK-R from the recovery key.
2. Authenticate and unwrap the vault-encryption key.
3. Derive a new KEK-M from the new master password.
4. Replace the master wrapper with a newly salted wrapper.
5. Preserve the recovery wrapper.
6. Do not re-encrypt every record or expose plaintext credentials.

### Manual lock and auto-lock

1. Stop accepting credential operations.
2. Invalidate the active vault-encryption-key reference.
3. Clear decrypted record objects where practical.
4. Return to the login screen.

### Credential update

1. Authenticate the active session.
2. Create a fresh nonce.
3. Encrypt the updated record with the vault-encryption key.
4. Commit the ciphertext atomically.
5. Do not reuse the prior record nonce.

## Tamper and failure behavior

- Any invalid AES-GCM tag must cause decryption failure.
- Invalid wrappers must not release the vault-encryption key.
- Invalid record ciphertext must not be displayed as partially decrypted data.
- A failed write must not silently replace valid ciphertext with incomplete data.
- Errors shown to the user must be generic and must not reveal key hierarchy details.
- Security diagnostics may identify a failure category internally only if they contain no secret values.

## Non-goals

- Custom cryptographic algorithms
- Custom key-stretching algorithms
- Storing the master password for convenience
- Storing the recovery key for automatic recovery
- Deriving the vault-encryption key directly from a user password
- Cloud key escrow or server-side recovery

