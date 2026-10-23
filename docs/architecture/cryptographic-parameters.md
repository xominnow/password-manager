# Cryptographic Parameters and Usage Rules

**Project:** Android Password Manager
**Related checklist task:** 2.4
**Status:** Draft for review

## Parameter-selection principle

The application will use established cryptographic primitives and record the parameters needed to interpret each protected value. The initial values below are a mobile-device baseline, not a substitute for benchmarking on the selected physical phone. Security parameters must not be weakened solely to improve responsiveness without updating the threat model and obtaining review approval.

## Argon2id configuration

### Initial baseline

| Parameter | Baseline |
|---|---:|
| Algorithm | Argon2id |
| Memory cost | 65,536 KiB / 64 MiB |
| Time cost | 3 iterations |
| Parallelism | 1 lane |
| Salt length | 16 random bytes |
| Output length | 32 bytes |
| Input encoding | UTF-8 for user-entered password; canonical bytes for recovery key |

The baseline must be benchmarked on the selected physical Android device. The final parameter record must include measured derivation time and device information. Any adjustment must preserve Argon2id and be documented as a security decision.

### Usage rules

- Use a fresh, independent salt for the master-password and recovery-key derivations.
- Store the algorithm identifier, version, and parameters with the protected wrapper metadata.
- Treat the master password as sensitive input and never write it to logs or persistent storage.
- Treat the recovery key as sensitive input and never copy it to the clipboard automatically.
- Derive raw 32-byte key-encryption keys through a vetted Argon2id API; do not use an encoded password hash string directly as an AES key.
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

The Python `cryptography` `AESGCM` interface is the planned implementation. Its output includes the authentication tag with the ciphertext; the storage format must document this representation.

### Nonce rules

- Generate a fresh random nonce for every encryption and key-wrapping operation.
- Never reuse a nonce with the same AES key.
- Persist each nonce with the corresponding ciphertext.
- Never derive a nonce from a password, record name, timestamp, or database identifier.
- A failed or interrupted operation must not cause a nonce to be reused.

### Associated-data rules

Authenticated but unencrypted associated data must bind ciphertext to its context. The canonical associated-data representation should include:

```text
format_version | vault_identifier | purpose | record_identifier | record_type
```

The exact serialization must be deterministic, versioned, and tested. Wrapper purpose must distinguish `master`, `recovery`, and `record` contexts. Associated data is not secret, but changing it must cause authentication failure.

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

1. Measure Argon2id derivation time on the physical test device.
2. Confirm setup and unlock remain usable without weakening the approved security floor.
3. Verify unique nonce generation across repeated encryptions.
4. Verify changed ciphertext, nonce, key, or associated data fails authentication.
5. Verify each wrapper purpose is domain-separated.
6. Record the final values and measurements in technical documentation.

## References

- `cryptography` authenticated encryption documentation: https://cryptography.io/en/stable/hazmat/primitives/aead/
- `argon2-cffi` documentation: https://argon2-cffi.readthedocs.io/en/stable/

