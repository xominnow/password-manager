# Scrypt Key Derivation

The filename is retained for historical links; the implemented KDF is Scrypt,
not Argon2id. See [current technical guide](TECHNICAL_DOCUMENTATION.md).

**Related checklist task:** 5.2  
**Status:** Draft for review

`app/security/kdf.py` uses the Scrypt KDF from `cryptography` to derive raw
32-byte key-encryption keys. It does not store or return an encoded
password-hash string. Scrypt was selected for the Android build because it is
provided by an already-required, established cryptographic library and avoids
an additional native package recipe.

## Approved baseline

| Parameter | Value |
|---|---:|
| Algorithm | Scrypt |
| `n` work factor | 65,536 minimum; power of two |
| `r` block size | 8 minimum |
| `p` parallelization | 1 minimum |
| Salt length | 16 bytes |
| Output length | 32 bytes |

The implementation permits stronger `n`, `r`, or `p` settings, but rejects
values below the approved floor. A separate fresh salt is required for the
master-password and recovery-key derivations.

## Input handling

- Master passwords are encoded as UTF-8.
- New recovery keys are supplied as 16 case-sensitive ASCII alphanumeric bytes;
  legacy Base32 keys decode to 32 bytes. Both formats remain accepted.
- Empty secrets and malformed salts are rejected.
- Secrets and derived keys are never logged or persisted by this module.

The baseline must still be benchmarked on the selected physical Android phone
before final security parameters are declared production-ready.
