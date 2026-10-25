# Credential Creation

**Related checklist task:** 6.1  
**Status:** Draft for review

`app/services/credentials.py` creates one encrypted credential entry for an
unlocked local session.

## Flow

1. Confirm that the session is unlocked.
2. Validate the app/website name, username, and password are present.
3. Generate a random UUID-style entry identifier.
4. Serialize the three fields canonically in transient memory.
5. Encrypt the payload with the session's vault key.
6. Bind the ciphertext to the vault identifier, entry identifier, record type,
   and record version through AES-GCM associated data.
7. Insert only the encrypted payload and metadata into SQLite.

The service returns a transient `CredentialRecord` for the caller. The
database never receives plaintext credential columns. Password-strength
feedback, viewing, editing, deletion, and UI integration remain separate
tasks.
