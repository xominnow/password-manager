# Master-Password Key Wrapping

**Related checklist task:** 5.4  
**Status:** Draft for review

`app/security/wrapping.py` wraps the random vault-encryption key with a
password-derived key-encryption key. The password is processed through the
approved Scrypt parameters, then AES-256-GCM encrypts the 32-byte vault key.

## Stored wrapper fields

- Wrapper format version
- Purpose: `master`
- Vault identifier
- Scrypt parameters
- Fresh 16-byte KDF salt
- Fresh 12-byte AES-GCM nonce
- Ciphertext with the authentication tag appended by `AESGCM`

The associated data is deterministic JSON containing the wrapper version,
purpose, and vault identifier. It is reconstructed during unwrapping so that a
wrapper moved to a different vault identifier fails authentication.

Wrong passwords, changed context, and tampered ciphertext all produce the same
generic `InvalidMasterWrapper` failure. Passwords, derived keys, plaintext
vault keys, and ciphertext are not logged by this implementation.

This task does not persist wrappers or implement recovery wrapping; recovery
wrapping uses a separate purpose and key-derivation path in the next task.
