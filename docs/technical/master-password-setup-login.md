# Master-Password Setup and Login

**Related checklist task:** 5.8  
**Status:** Draft for review

`app/security/vault_service.py` coordinates first-time local setup and normal
master-password login.

## Setup

1. Validate the master password against the approved minimum policy.
2. Generate a random 16-byte vault identifier and 256-bit vault key.
3. Generate a 16-character case-sensitive alphanumeric recovery key.
4. Create independent master and recovery wrappers.
5. Insert vault metadata and both wrappers atomically.
6. Return the formatted recovery key to the setup flow for secure display and
   confirmation.

The recovery key is not persisted by the service. The master password is not
persisted, logged, or returned.

## Login

The service loads only the master wrapper metadata, derives a KEK from the
entered password, and authenticates the wrapper. Successful login returns an
in-memory `UnlockedVaultSession`; failure returns a generic authentication
error. Calling `lock()` removes the session's active key reference.

Automatic locking, recovery reset, UI confirmation and credential CRUD are now
integrated. See [current technical guide](TECHNICAL_DOCUMENTATION.md).
