# Database Design

**Project:** Android Password Manager
**Related checklist task:** 2.5
**Status:** Draft for review

## Storage approach

The application will use a local SQLite database stored inside Android application-private storage. SQLite provides persistence and transactions; application-level AES-256-GCM protects vault data. The database must not be treated as a plaintext credential store.

## Design principles

- Store plaintext credentials only in transient application memory during an authenticated operation.
- Store encrypted credential payloads as binary blobs.
- Store non-secret cryptographic metadata required for decryption and migration.
- Keep the app/website name inside the encrypted entry payload so search does not require a plaintext name index.
- Use UUID-style entry identifiers that do not contain credential names.
- Use transactions for initialization, reset, create, update, and delete operations.
- Enable foreign-key enforcement on every database connection.
- Reject unknown schema or cryptographic format versions.

## Logical schema

### `vault_metadata`

Singleton table containing vault-level identity and format metadata.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | INTEGER | Primary key; must equal `1` | Enforces one vault per local app installation. |
| `vault_id` | BLOB | Required; unique | Random non-secret vault identifier used in associated data. |
| `format_version` | INTEGER | Required | Version of the vault metadata format. |
| `created_at` | TEXT | Required | ISO-8601 creation timestamp. |
| `updated_at` | TEXT | Required | ISO-8601 metadata update timestamp. |

### `key_wrappers`

Stores independent encrypted wrappers for the random vault-encryption key.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | INTEGER | Primary key | Wrapper identifier. |
| `vault_id` | BLOB | Required; foreign key | Links to `vault_metadata`. |
| `purpose` | TEXT | Required; `master` or `recovery` | Separates wrapper domains. |
| `format_version` | INTEGER | Required | Wrapper serialization version. |
| `kdf_algorithm` | TEXT | Required | Expected value: `argon2id`. |
| `kdf_memory_cost` | INTEGER | Required | Argon2id memory parameter in KiB. |
| `kdf_time_cost` | INTEGER | Required | Argon2id time parameter. |
| `kdf_parallelism` | INTEGER | Required | Argon2id parallelism parameter. |
| `kdf_salt` | BLOB | Required | Unique salt for this wrapper. |
| `encryption_algorithm` | TEXT | Required | Expected value: `aes-256-gcm`. |
| `nonce` | BLOB | Required | Unique AES-GCM nonce for this wrapper. |
| `wrapped_key` | BLOB | Required | Encrypted vault-encryption key with authentication tag. |
| `aad_version` | INTEGER | Required | Associated-data serialization version. |
| `created_at` | TEXT | Required | Wrapper creation timestamp. |
| `updated_at` | TEXT | Required | Wrapper update timestamp. |

Unique constraint: `(vault_id, purpose)`.

### `entries`

Stores encrypted credential payloads.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | TEXT | Primary key | Random UUID-style identifier. |
| `vault_id` | BLOB | Required; foreign key | Links to `vault_metadata`. |
| `record_version` | INTEGER | Required | Encrypted-entry payload version. |
| `nonce` | BLOB | Required | Unique AES-GCM nonce for the record. |
| `ciphertext` | BLOB | Required | Encrypted app/website name, username, and password with tag. |
| `created_at` | TEXT | Required | Creation timestamp. |
| `updated_at` | TEXT | Required | Last update timestamp. |

The app/website name is not stored as a plaintext column. Search decrypts records only after the vault is unlocked.

### `schema_migrations`

Tracks database-format migrations without containing user credentials.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `version` | INTEGER | Primary key | Applied schema version. |
| `applied_at` | TEXT | Required | Migration timestamp. |

## Encrypted entry payload

The plaintext payload exists only transiently before encryption and after authenticated decryption:

```json
{
  "app_name": "Example App",
  "username": "demo-user",
  "password": "synthetic-test-password"
}
```

The serialized representation must be canonical and versioned before AES-GCM encryption. The ciphertext is authenticated with associated data containing the vault identifier, entry identifier, record type, and record version.

## Representative DDL

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE vault_metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    vault_id BLOB NOT NULL UNIQUE,
    format_version INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE key_wrappers (
    id INTEGER PRIMARY KEY,
    vault_id BLOB NOT NULL REFERENCES vault_metadata(vault_id),
    purpose TEXT NOT NULL CHECK (purpose IN ('master', 'recovery')),
    format_version INTEGER NOT NULL,
    kdf_algorithm TEXT NOT NULL,
    kdf_memory_cost INTEGER NOT NULL,
    kdf_time_cost INTEGER NOT NULL,
    kdf_parallelism INTEGER NOT NULL,
    kdf_salt BLOB NOT NULL,
    encryption_algorithm TEXT NOT NULL,
    nonce BLOB NOT NULL,
    wrapped_key BLOB NOT NULL,
    aad_version INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (vault_id, purpose)
);

CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    vault_id BLOB NOT NULL REFERENCES vault_metadata(vault_id),
    record_version INTEGER NOT NULL,
    nonce BLOB NOT NULL,
    ciphertext BLOB NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
```

## Transaction rules

- Vault initialization commits metadata and both key wrappers atomically.
- Recovery reset commits the new master wrapper atomically and preserves the recovery wrapper.
- Entry create and update commit ciphertext and timestamps in one transaction.
- Entry deletion requires explicit confirmation and commits as one transaction.
- Failed transactions must roll back without replacing valid ciphertext.
- Database writes must not log plaintext payloads.

## Search behavior

Phase one will not maintain a plaintext app-name index. After authentication, the application may decrypt records in memory, compare app/website names, and display matching results. The design favors reduced metadata leakage over database-level plaintext search performance.

## Backup boundary

Encrypted export/import is not part of the current phase-one MVP schema. If added later, it must preserve the same vault-key and authentication model and receive a new requirements and threat-model review.

