# Credential Search

**Related checklist task:** 6.5  
**Status:** Implemented in the service layer; UI search control remains part of later Phase 6 integration.

Credential app/website names remain inside AES-GCM-encrypted payloads. The
database therefore does not expose searchable plaintext columns or perform
SQL text matching. `CredentialService.search()` first requires an unlocked
session, loads only encrypted payloads belonging to the authenticated vault,
decrypts them in memory, and filters the resulting app names.

Search behavior is a trimmed, case-insensitive substring match. An empty query
returns all entries. Results are deterministically sorted by app name and entry
identifier, and each result is a password-masked `CredentialView`.

Authentication failures, malformed payloads, and tampering produce a generic
`CredentialReadError` rather than partial results. Non-text queries and locked
sessions are rejected before searching.
