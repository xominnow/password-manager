# Vault-Key Creation

**Related checklist task:** 5.3  
**Status:** Draft for review

`app/security/keys.py` represents the vault-encryption key as an immutable
`VaultKey` object. `create_vault_key()` obtains 32 random bytes from the secure
randomness module and validates the format version and key length.

The vault key is independent of the master password and recovery key. Later
tasks will wrap it separately with the master-derived and recovery-derived key-
encryption keys. This module does not persist, encrypt, log, or serialize the
key. Its default representation omits the key bytes to reduce accidental
disclosure through debugging or logs.

Python cannot guarantee immediate memory zeroization for immutable `bytes`
objects. Session lifecycle and memory-clearing limitations will be documented
when the authenticated vault session is implemented.
