# Encrypted SQLite Storage

**Related checklist task:** 5.7  
**Status:** Draft for review

`app/storage/sqlite.py` manages the local SQLite schema. SQLite stores vault
metadata, wrapper metadata/ciphertext, and encrypted entry payloads; it does
not store app names, usernames, or passwords in plaintext columns.

## Storage rules

- Foreign-key enforcement is enabled for every connection.
- Initialization inserts the singleton vault metadata and both wrappers in one
  transaction.
- Entry inserts, updates, and deletes use transactions.
- Entry rows contain only identifiers, versions, nonces, ciphertext, and
  timestamps.
- Wrapper rows store KDF and AES-GCM metadata plus wrapped-key ciphertext.
- Unknown future schema versions are rejected.
- Failed transactions roll back through SQLite's context manager.

The database layer accepts only already-encrypted `EncryptedPayload` objects.
Plaintext credential serialization belongs to a later application-service task
and must occur only transiently before encryption.

For current wrapper APIs, the binary database `vault_id` is represented in
authenticated wrapper context as `vault_id.hex()`. This keeps the database
identifier binary while producing a deterministic text context for the wrapper
associated data.
