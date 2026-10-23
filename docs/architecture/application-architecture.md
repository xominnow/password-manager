# Application Architecture and Module Boundaries

**Project:** Android Password Manager
**Related checklist task:** 2.2
**Status:** Draft for review

## Architectural style

The application will use a layered, local-first architecture with explicit separation between presentation, application services, domain/security logic, storage, and Android platform adapters.

## Layer diagram

```text
┌──────────────────────────────────────────────┐
│ Presentation layer                           │
│ Kivy screens, forms, dialogs, navigation     │
└──────────────────────┬───────────────────────┘
                       │ user actions / view state
                       ▼
┌──────────────────────────────────────────────┐
│ Application layer                            │
│ session, vault, credential, generator flows │
└───────────────┬───────────────┬──────────────┘
                │               │
                ▼               ▼
┌──────────────────────┐  ┌──────────────────────┐
│ Security core        │  │ Platform adapters    │
│ KDF, keys, AES-GCM,  │  │ clipboard, secure    │
│ authentication       │  │ window, timing       │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           ▼                         │
┌────────────────────────────────────┴─────────┐
│ Storage layer                                 │
│ SQLite repository, serialization, transactions│
└───────────────────────────────────────────────┘
```

## Proposed module structure

```text
app/
├── main.py                 # Kivy application entry point
├── ui/                     # Screens, widgets, dialogs, and view models
├── services/               # User-facing application workflows
├── domain/                 # Credential and vault data models
├── security/               # KDF, key hierarchy, encryption, validation
├── storage/                # SQLite connection, schema, repositories
├── platform/               # Clipboard, secure-window, and Android adapters
└── config/                 # Versioned settings and non-secret defaults
```

## Module responsibilities

### `main.py`

- Creates the Kivy application.
- Configures startup and screen navigation.
- Does not implement cryptography or direct SQL queries.

### `ui/`

- Renders approved screens and mockups.
- Collects user input and displays non-sensitive status messages.
- Sends actions to application services.
- Does not derive keys, encrypt data, or construct SQL statements.

### `services/`

- Coordinates setup, login, recovery, CRUD, generation, lock, and clipboard workflows.
- Owns session-state transitions.
- Converts domain and security results into UI-safe outcomes.
- Does not expose raw cryptographic exceptions or sensitive diagnostic values to the UI.

### `domain/`

- Defines typed representations for vault entries, session state, and metadata.
- Contains validation rules that do not require cryptographic primitives.
- Does not know about Kivy or SQLite implementation details.

### `security/`

- Generates keys and random values.
- Derives master and recovery key-encryption keys.
- Wraps and unwraps the vault-encryption key.
- Encrypts and decrypts vault records.
- Validates authentication tags and versioned security metadata.
- Must not import UI, platform adapters, or application navigation code.

### `storage/`

- Owns SQLite schema, connections, transactions, and repositories.
- Persists ciphertext, nonces, tags, salts, KDF parameters, and non-secret metadata.
- Does not receive or persist plaintext passwords outside the shortest necessary transaction boundary.
- Must not implement key derivation or user-interface behavior.

### `platform/`

- Encapsulates clipboard access and clearing.
- Encapsulates Android secure-window behavior.
- Provides platform-aware timing or lifecycle hooks where needed.
- Keeps Android-specific calls out of security and domain modules.

### `config/`

- Defines versioned, non-secret application settings.
- Does not contain passwords, recovery keys, vault files, signing keys, or machine-specific secrets.

## Dependency rules

```text
ui → services → domain
              ├→ security
              ├→ storage
              └→ platform
security → domain/config only
storage  → domain/config only
platform → config and Android/Python platform APIs
```

- Dependencies point inward toward stable interfaces.
- Security code must not depend on UI state.
- Storage code must not decide authentication or session policy.
- UI code must not access SQLite directly.
- No network client or remote service is part of phase one.
- Cross-layer calls should use explicit interfaces so unit tests can substitute fakes.

## Sensitive-data flow

1. UI collects a value and passes it to an application service.
2. The service validates the request and calls the security core.
3. The security core encrypts or derives only what is required.
4. Storage persists ciphertext and metadata.
5. The service returns a minimal success or failure result.
6. UI renders the result without receiving unnecessary key material.

## Session boundary

The application service owns whether the vault is locked or unlocked. A locked session must prevent credential operations. Auto-lock and manual lock must clear or invalidate active session references before returning to the login screen.

## Test boundary

Each layer must be testable independently:

- UI tests validate navigation and user-visible behavior.
- Service tests validate workflows with fake security/storage/platform adapters.
- Security tests validate cryptographic invariants and failure behavior.
- Storage tests validate schema, transactions, and ciphertext persistence.
- Platform tests validate clipboard and secure-window adapters on Android.

