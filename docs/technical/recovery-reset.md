# Recovery-Key Master-Password Reset

**Related checklist task:** 5.9  
**Status:** Draft for review

`LocalVaultService.reset_master_password()` authenticates the stored recovery
wrapper and uses the recovered vault key to create a new master wrapper.

## Transaction flow

1. Validate the proposed new master password.
2. Load and validate the recovery wrapper.
3. Decode the user-provided recovery key into canonical bytes.
4. Authenticate and unwrap the vault key.
5. Create a new master wrapper with a fresh Scrypt salt and AES-GCM nonce.
6. Replace only the master-wrapper row in one SQLite transaction.
7. Preserve the recovery wrapper and return an unlocked session.

The encrypted credential entries are not re-encrypted because their vault key
does not change. Invalid recovery input produces a generic failure and does
not modify the master wrapper.
