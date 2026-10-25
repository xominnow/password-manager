# Recovery-Key Wrapping

**Related checklist task:** 5.5  
**Status:** Draft for review

`app/security/wrapping.py` provides an independent recovery wrapper for the
same random vault-encryption key. New recovery keys are decoded to canonical
16-character material before Scrypt derives a recovery key-encryption key; the
decoder retains compatibility with the previous 32-byte Base32 format.

The recovery wrapper has its own fresh salt and nonce and authenticates
associated data containing the wrapper version, `recovery` purpose, and vault
identifier. It cannot be substituted for the master wrapper because the
purpose is authenticated and the two derivations use independent salts.

The recovery key is not stored by the wrapper. Callers must protect the
user-readable recovery key and must not log or copy it automatically. The UI
may copy it only after an explicit user action and clears the app-owned
clipboard value after the normal timeout.
