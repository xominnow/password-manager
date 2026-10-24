# Security-Core Test Coverage

**Related checklist task:** 5.10  
**Status:** Draft for review

The security-core suite covers both isolated primitives and integrated local
vault behavior:

- CSPRNG output lengths and recovery-key format validation
- Scrypt parameter floors, salt handling, and deterministic derivation
- Vault-key length, immutability, and disclosure-safe representation
- Master and recovery wrapper round trips and tamper rejection
- AES-GCM nonce freshness, associated-data binding, and tag failures
- SQLite schema constraints, foreign keys, and transaction behavior
- Master setup, login, session lock, and recovery reset
- End-to-end encrypted entry round trips
- Plaintext credential, master-password, and recovery-key storage invariants

Run the full suite from the project root:

```powershell
pytest -q
```

The suite uses synthetic credentials only. It does not test production Android
keystore behavior, secure memory zeroization, or physical-device performance;
those remain release-validation tasks.
