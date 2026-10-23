# System Architecture Diagram

**Project:** Android Password Manager
**Related checklist task:** 2.7
**Status:** Draft for review

## Architecture overview

```mermaid
flowchart TB
    User[Single local user]
    Android[Android device\nAPI 26+]
    UI[Kivy presentation layer\nScreens, forms, dialogs]
    Services[Application services\nSetup, login, recovery, CRUD, lock]
    Domain[Domain models\nVault entry and session state]
    Security[Security core\nArgon2id, key wrapping, AES-256-GCM]
    Platform[Platform adapters\nClipboard, secure window, lifecycle, clock]
    Storage[SQLite storage layer\nTransactions and repositories]
    DB[(App-private SQLite database\nCiphertext and metadata only)]
    AndroidAPIs[Android platform APIs\nClipboard, secure window, lifecycle]

    User --> Android
    Android --> UI
    UI --> Services
    Services --> Domain
    Services --> Security
    Services --> Storage
    Services --> Platform
    Security --> Storage
    Storage --> DB
    Platform --> AndroidAPIs

    classDef sensitive fill:#fff0f0,stroke:#b33,stroke-width:1px;
    class Security,DB sensitive;
```

## Data and trust boundaries

```mermaid
flowchart LR
    Input[User input\nmaster password, recovery key, entries]
    Service[Application service\nvalidates workflow and session]
    KDF[Argon2id\nkey derivation]
    Wrap[AES-256-GCM\nkey wrapping]
    VaultKey[Random vault-encryption key\nactive session only]
    Record[AES-256-GCM\nrecord encryption]
    SQLite[(SQLite\nciphertext + metadata)]
    Clipboard[Android clipboard\n30-second timeout]
    Screen[Android secure window\nscreenshot protection]

    Input --> Service
    Service --> KDF
    KDF --> Wrap
    Wrap --> VaultKey
    VaultKey --> Record
    Record --> SQLite
    Service --> Clipboard
    Service --> Screen

    boundary1{{Application boundary}}
    boundary2{{Android platform boundary}}
    Service --- boundary1
    Clipboard --- boundary2
    Screen --- boundary2
```

## Component responsibilities

| Component | Responsibility | Sensitive-data rule |
|---|---|---|
| Kivy presentation | Display approved screens and collect actions | Must not implement cryptography or direct SQL. |
| Application services | Coordinate workflows and session policy | Must return minimal UI-safe results. |
| Domain models | Represent entries and session state | Must not persist plaintext by themselves. |
| Security core | Derive keys, wrap keys, encrypt records, verify tags | Must not import UI code. |
| Storage layer | Persist ciphertext and metadata transactionally | Must never store plaintext credentials. |
| Platform adapters | Encapsulate clipboard, secure-window, clock, and lifecycle APIs | Must not log copied passwords or keys. |
| SQLite database | Store encrypted records and required metadata | Located in Android app-private storage. |

## Core data flow

1. The user supplies input through the Kivy interface.
2. An application service validates the requested workflow and session state.
3. The security core derives or unwraps keys as required.
4. Credential payloads are encrypted and authenticated before storage.
5. The storage layer commits ciphertext and metadata in a transaction.
6. The service returns a minimal result to the UI.
7. Locking invalidates the active session and returns the app to the login screen.

## Deployment boundary

```text
Python source
    │
    ▼
Kivy application
    │ Buildozer / python-for-android
    ▼
Private debug APK
    │
    ▼
Physical Android device
```

The phase-one application is local-only and requests no Internet permission. The public GitHub repository stores source and documentation, not vault data or secrets.

## References to detailed designs

- [Application architecture](application-architecture.md)
- [Vault-key architecture](vault-key-architecture.md)
- [Database schema](../database/schema.md)
- [Session and platform controls](session-and-platform-controls.md)
- [Threat model](threat-model.md)

