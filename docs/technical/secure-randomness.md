# Secure Randomness

**Related checklist task:** 5.1  
**Status:** Draft for review

`app/security/randomness.py` uses Python's `secrets.token_bytes`, which
delegates to the operating system's cryptographically secure random source.
No custom pseudo-random generator, timestamp, password, identifier, or other
predictable input is used.

## Generated material

- Vault-encryption key: 32 random bytes / 256 bits
- AES-GCM nonce: 12 random bytes / 96 bits per encryption operation
- Recovery key: 16 cryptographically random alphanumeric characters

New recovery keys are canonicalized as 16 ASCII alphanumeric characters before
Scrypt derivation. The decoder also accepts the previous 52-character Base32
format so existing vaults remain recoverable. The plaintext recovery key must
not be stored or logged; copying is available only after an explicit user
action and is cleared by the normal clipboard timeout.

## Scope boundary

This task provides random-material generation only. Key derivation, AES-GCM
encryption, storage, authentication, and recovery workflows remain separate
tasks and must use fresh material from this module where applicable.
