# AES-256-GCM Encryption and Authentication

**Related checklist task:** 5.6  
**Status:** Draft for review

`app/security/aead.py` centralizes authenticated encryption for vault data and
key wrappers using the `cryptography` library's `AESGCM` implementation.

## Rules enforced by the module

- AES-256 keys must be exactly 32 bytes.
- Every encryption receives a fresh 12-byte nonce from the secure-randomness
  module.
- Associated data is required and cannot be empty.
- The authentication tag is appended to the ciphertext by `AESGCM` and is
  validated before plaintext is returned.
- Invalid tags, changed context, wrong keys, and tampered ciphertext produce a
  generic `InvalidCiphertext` error.
- Decryption never returns partially authenticated plaintext.

The encrypted payload stores the nonce, ciphertext, and format version. The
caller is responsible for deterministically reconstructing the same associated
data during decryption and persisting the payload atomically.
