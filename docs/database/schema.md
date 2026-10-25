# Database Design

**Project:** Android Password Manager
**Related checklist tasks:** 2.5, 9.3
**Status:** Source-reconciled schema reference, 2026-10-24; awaiting task approval.

## Storage approach

The app uses `Path(App.user_data_dir) / "vault.sqlite3"` in Android application
storage. `app/storage/sqlite.py` owns DDL and SQL. SQLite provides persistence
and transactions; application-level AES-256-GCM protects credential fields.
This is not whole-database encryption: IDs, salts, nonces, algorithms, versions,
timestamps and row counts remain visible. No plaintext name index is stored.

## Format versions and relationships

Database schema and vault metadata version are 2; encrypted record and wrapper
formats are 1. These are distinct version domains, not interchangeable numbers.
The wrapper `aad_version` must match its wrapper `format_version`.

See the [entity relationship diagram](DATABASE_DESIGN_REVIEW.md). A vault has
zero or more entries and, after successful service setup, exactly two wrappers
(one master, one recovery). The schema permits zero to two wrappers via purpose
and uniqueness constraints; service initialization enforces exactly two.
`schema_migrations` is independent of vault rows and has no foreign key.

## Design principles

- Store plaintext credentials only in transient application memory during an authenticated operation.
- Store encrypted credential payloads as binary blobs.
- Store non-secret cryptographic metadata required for decryption and migration.
- Keep the app/website name inside the encrypted entry payload so search does not require a plaintext name index.
- Use UUID-style entry identifiers that do not contain credential names.
- Use transactions for initialization, reset, create, update, and delete operations.
- Enable foreign-key enforcement on every database connection.
- Reject future schema-ledger versions and unsupported cryptographic payload/
  wrapper versions. Vault metadata version is stored but is not separately
  exhaustively validated by all read paths; do not infer universal version rejection.

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
| `kdf_algorithm` | TEXT | Required | Expected value: `scrypt`. |
| `kdf_n` | INTEGER | Required | Scrypt work-factor parameter; baseline `65536`. |
| `kdf_r` | INTEGER | Required | Scrypt block-size parameter; baseline `8`. |
| `kdf_p` | INTEGER | Required | Scrypt parallelization parameter; baseline `1`. |
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

Records schema version without containing user credentials. Current startup
creates tables if absent, records version 2 if the ledger is empty, and rejects
a highest recorded version greater than 2. It does not run numbered migrations
or upgrade an older ledger through a complete version-by-version process.

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

Serialization is UTF-8 JSON with sorted keys, compact separators, and
`ensure_ascii=False`. Entry authenticated data is canonical JSON with
`format_version` (1), `record_id`, `record_type` (`credential`), and `vault_id`
(hex). The record version is stored alongside ciphertext, not inserted into
the credential JSON. A 12-byte nonce and ciphertext (including 16-byte tag)
are stored separately. Wrapper associated data uses `format_version`, `purpose`
and hex `vault_id`. Do not alter serialization/context without a compatibility plan.

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
    kdf_n INTEGER NOT NULL,
    kdf_r INTEGER NOT NULL,
    kdf_p INTEGER NOT NULL,
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

Schema creation/ledger setup occurs when the database opens, before the later
vault-initialization transaction. A ledger row can therefore exist without a
configured vault. User confirmation and authenticated-session validation belong
to UI/services; SQLite does not itself authenticate callers. Service creation
uses `uuid.uuid4().hex` IDs; random nonce lengths and supported crypto fields
are validated by application types. Nonce uniqueness is not a database constraint.

## Search behavior

After authentication, the credential service decrypts all vault entries in
memory and matches trimmed/casefolded substrings of app/website names. Empty
queries return all entries; results sort by casefolded name then ID. Search
is linear in vault size, and is repeated on input changes. Username/password
search and database-level plaintext indexing are not implemented.

## Failure, deletion, and verification limits

Foreign keys are enabled per connection and updates/deletes scope by entry ID
and vault ID. SQL values use placeholders. Authentication-tag failure prevents
decrypted records from being returned. Missing wrappers prevent normal unlock
or recovery. Schema initialization is not a general atomic migration framework.
SQLite delete is logical removal; no VACUUM/secure-delete or physical-media
erasure guarantee is provided. Full row rollback/replay and hostile metadata
changes are not universally prevented by encrypting individual payloads.

See [final results](../testing/final-test-results.md) for local disk/tamper tests
and outstanding physical/release identity checks. In-memory and source tests do
not establish every crash/power-loss/migration behavior.

## Backup boundary

Encrypted export/import is not part of the current phase-one MVP schema. If added later, it must preserve the same vault-key and authentication model and receive a new requirements and threat-model review.

