# Credential Deletion and Confirmation

**Related checklist task:** 6.4  
**Status:** Implemented in the service layer; UI confirmation remains part of later Phase 6 integration.

`CredentialService.delete()` requires an unlocked vault session, a valid entry
identifier, and an explicit `confirmed=True` keyword. The default is safe:
omitting confirmation raises `CredentialValidationError` and leaves the entry
unchanged.

After confirmation, deletion is executed by the SQLite transaction-backed
storage method with both the entry identifier and the authenticated vault ID.
This prevents the service from deleting an entry belonging to another vault.
The method returns `True` when one record was removed and `False` when the
entry is not available in the selected vault. No plaintext credential data is
needed for deletion.

The UI must obtain confirmation immediately before calling the service and
must not treat a cancelled confirmation as a deletion. Tests cover cancelled
deletion, successful deletion, missing entries, locked sessions, invalid entry
identifiers, and strict confirmation handling.
