# Cryptographic Parameters and Usage Rules

**Project:** Android Password Manager
**Related checklist task:** 2.4
**Status:** Implementation-aligned 2026-10-24; see [security decisions](security-decisions.md).

## Parameter-selection principle

The application uses established cryptographic primitives and stores parameters
needed to interpret protected values. The values below are implemented; dedicated
Scrypt timing on the phone remains unrecorded. Security parameters must not be
weakened solely to improve responsiveness without updating the threat model.

## Scrypt configuration

### Initial baseline

| Parameter | Baseline |
|---|---:|
| Algorithm | Scrypt |
| `n` work factor | 65,536 |
| `r` block size | 8 |
| `p` parallelization | 1 |
| Salt length | 16 random bytes |
| Output length | 32 bytes |
| Input encoding | UTF-8 for user-entered password; canonical bytes for recovery key |

The baseline must be benchmarked on the selected physical Android device. The final parameter record must include measured derivation time and device information. Any adjustment must preserve the approved Scrypt floor and be documented as a security decision.

### Usage rules

- Use a fresh, independent salt for the master-password and recovery-key derivations.
- Store the algorithm identifier, version, and parameters with the protected wrapper metadata.
- Treat the master password as sensitive input and never write it to logs or persistent storage.
- Treat the recovery key as sensitive input and never copy it to the clipboard automatically.
- Derive raw 32-byte key-encryption keys through the vetted Scrypt API in `cryptography`; do not use an encoded password hash string directly as an AES key.
- Authenticate the resulting wrapper before releasing the vault-encryption key.
- Do not silently accept unsupported or weakened parameter values.

## AES-256-GCM configuration

| Parameter | Required value |
|---|---:|
| Algorithm | AES-GCM |
| Key length | 256 bits / 32 bytes |
| Nonce length | 12 random bytes |
| Authentication tag | 16 bytes / 128 bits |
| Key source | Random vault-encryption key or derived key-encryption key |

The implemented `cryptography` `AESGCM` interface appends its tag to ciphertext;
the nonce is stored separately. New recovery keys have 16 case-sensitive ASCII
alphanumeric characters (approximately 95.3 bits of random choice), not 256 bits.
Legacy recovery keys still decode to 32 bytes. See [recovery design](recovery-key-design.md).

### Nonce rules

- Generate a fresh random nonce for every encryption and key-wrapping operation.
- Never reuse a nonce with the same AES key.
- Persist each nonce with the corresponding ciphertext.
- Never derive a nonce from a password, record name, timestamp, or database identifier.
- A failed or interrupted operation must not cause a nonce to be reused.

### Associated-data rules

Authenticated but unencrypted associated data binds ciphertext to its context.
Current canonical JSON dictionaries use sorted keys and compact separators:

```text
Wrapper: format_version, purpose (master/recovery), vault_id (hex)
Record:  format_version, record_id, record_type (credential), vault_id (hex)
```

Wrappers and records have separate context dictionaries, both at version 1.
Changing reconstructed associated data causes authentication failure. KDF costs
and salts are not direct fields in these dictionaries; deriving the correct
key is necessary for successful authentication. Individual authenticated records
do not establish rollback protection for an entire database.

### Decryption rules

- Do not use any decrypted bytes before the AES-GCM authentication tag has been verified.
- Treat authentication failure as a generic invalid-vault or invalid-record error.
- Do not display partially decrypted data.
- Reject unknown algorithm versions or malformed nonce/tag lengths.

## Key-use separation

- KEK-M protects only the vault-encryption key through the master wrapper.
- KEK-R protects only the vault-encryption key through the recovery wrapper.
- The vault-encryption key protects vault records.
- No key may be reused across unrelated purposes without explicit domain separation through associated data and wrapper purpose.

## Benchmark and validation requirements

Before implementation parameters are locked:

1. Measure Scrypt derivation time on the physical test device.
2. Confirm setup and unlock remain usable without weakening the approved security floor.
3. Verify unique nonce generation across repeated encryptions.
4. Verify changed ciphertext, nonce, key, or associated data fails authentication.
5. Verify each wrapper purpose is domain-separated.
6. Record the final values and measurements in technical documentation.

## References

- `cryptography` authenticated encryption documentation: https://cryptography.io/en/stable/hazmat/primitives/aead/
- `cryptography` KDF documentation: https://cryptography.io/en/stable/hazmat/primitives/kdf/

