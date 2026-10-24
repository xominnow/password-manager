# Credential Editing

**Related checklist task:** 6.3  
**Status:** Implemented in the service layer; UI integration remains a later Phase 6 task.

`CredentialService.update()` edits an existing credential only for an unlocked
vault session. The entry identifier remains unchanged, so authenticated data
continues to bind the record to the same vault and identity.

The replacement fields are validated and serialized in memory. The service
then encrypts the complete replacement payload with AES-256-GCM. Encryption
generates a fresh nonce for every update. SQLite receives only the new nonce,
ciphertext, and format metadata through its transaction-scoped update method;
plaintext credential fields are never stored in the database.

An update that targets an entry outside the selected vault or a nonexistent
entry is reported as `CredentialNotFoundError`. Locked sessions and invalid
fields are rejected before database mutation. Tests verify identifier reuse,
nonce replacement, ciphertext replacement, successful authenticated viewing,
missing-entry handling, lock handling, and field validation.
