"""SQLite persistence for encrypted vault metadata and payloads."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.security.aead import EncryptedPayload
from app.security.wrapping import MasterKeyWrapper, RecoveryKeyWrapper


SCHEMA_VERSION = 2
RECORD_VERSION = 1


class DatabaseError(ValueError):
    """Base error for invalid vault database operations."""


class UnsupportedSchemaError(DatabaseError):
    """Raised when a database is newer than this application supports."""


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _require_bytes(value: bytes, field_name: str) -> None:
    if not isinstance(value, bytes) or not value:
        raise DatabaseError(f"{field_name} must be non-empty bytes")


def _require_entry_id(entry_id: str) -> None:
    if not isinstance(entry_id, str) or not entry_id:
        raise DatabaseError("entry_id must be non-empty text")


class VaultDatabase:
    """Connection wrapper enforcing the local encrypted-vault schema."""

    def __init__(self, path: str | Path):
        self.path = path
        self._connection = sqlite3.connect(str(path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    @property
    def connection(self) -> sqlite3.Connection:
        """Expose the connection for diagnostics and controlled migrations."""

        return self._connection

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "VaultDatabase":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def _create_schema(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS vault_metadata (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    vault_id BLOB NOT NULL UNIQUE,
                    format_version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS key_wrappers (
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

                CREATE TABLE IF NOT EXISTS entries (
                    id TEXT PRIMARY KEY,
                    vault_id BLOB NOT NULL REFERENCES vault_metadata(vault_id),
                    record_version INTEGER NOT NULL,
                    nonce BLOB NOT NULL,
                    ciphertext BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
                """
            )
            versions = self._connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
            ).fetchone()
            if versions and versions["version"] > SCHEMA_VERSION:
                raise UnsupportedSchemaError("database schema is newer than this app")
            if not versions:
                self._connection.execute(
                    "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                    (SCHEMA_VERSION, _timestamp()),
                )

    def foreign_keys_enabled(self) -> bool:
        return self._connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    def get_vault_id(self) -> bytes | None:
        row = self._connection.execute(
            "SELECT vault_id FROM vault_metadata WHERE id = 1"
        ).fetchone()
        return None if row is None else bytes(row["vault_id"])

    def initialize_vault(
        self,
        vault_id: bytes,
        wrappers: Iterable[MasterKeyWrapper | RecoveryKeyWrapper],
    ) -> None:
        """Atomically insert metadata and exactly one wrapper per purpose."""

        _require_bytes(vault_id, "vault_id")
        wrapper_list = tuple(wrappers)
        purposes = {wrapper.purpose for wrapper in wrapper_list}
        if len(wrapper_list) != 2 or purposes != {"master", "recovery"}:
            raise DatabaseError("vault initialization requires master and recovery wrappers")

        vault_context = vault_id.hex()
        for wrapper in wrapper_list:
            if wrapper.vault_id != vault_context:
                raise DatabaseError("wrapper vault context does not match vault metadata")

        now = _timestamp()
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO vault_metadata(id, vault_id, format_version, created_at, updated_at)
                VALUES (1, ?, ?, ?, ?)
                """,
                (vault_id, SCHEMA_VERSION, now, now),
            )
            for wrapper in wrapper_list:
                self._insert_wrapper(vault_id, wrapper, now)

    def _insert_wrapper(
        self,
        vault_id: bytes,
        wrapper: MasterKeyWrapper | RecoveryKeyWrapper,
        timestamp: str,
    ) -> None:
        parameters = wrapper.kdf_parameters
        self._connection.execute(
            """
            INSERT INTO key_wrappers(
                vault_id, purpose, format_version, kdf_algorithm,
                kdf_n, kdf_r, kdf_p, kdf_salt,
                encryption_algorithm, nonce, wrapped_key, aad_version,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vault_id,
                wrapper.purpose,
                wrapper.format_version,
                parameters.algorithm,
                parameters.n,
                parameters.r,
                parameters.p,
                wrapper.kdf_salt,
                "aes-256-gcm",
                wrapper.nonce,
                wrapper.ciphertext,
                wrapper.format_version,
                timestamp,
                timestamp,
            ),
        )

    def list_wrappers(self) -> tuple[sqlite3.Row, ...]:
        rows = self._connection.execute(
            "SELECT * FROM key_wrappers ORDER BY purpose"
        ).fetchall()
        return tuple(rows)

    def get_wrapper(self, purpose: str) -> sqlite3.Row | None:
        if purpose not in {"master", "recovery"}:
            raise DatabaseError("unsupported wrapper purpose")
        return self._connection.execute(
            "SELECT * FROM key_wrappers WHERE purpose = ?",
            (purpose,),
        ).fetchone()

    def replace_master_wrapper(self, vault_id: bytes, wrapper: MasterKeyWrapper) -> None:
        """Replace only the master wrapper in one atomic transaction."""

        _require_bytes(vault_id, "vault_id")
        if not isinstance(wrapper, MasterKeyWrapper):
            raise DatabaseError("master wrapper is required")
        if wrapper.vault_id != vault_id.hex():
            raise DatabaseError("wrapper vault context does not match vault metadata")
        parameters = wrapper.kdf_parameters
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE key_wrappers
                SET format_version = ?, kdf_algorithm = ?, kdf_n = ?,
                    kdf_r = ?, kdf_p = ?, kdf_salt = ?,
                    encryption_algorithm = ?, nonce = ?, wrapped_key = ?,
                    aad_version = ?, updated_at = ?
                WHERE vault_id = ? AND purpose = 'master'
                """,
                (
                    wrapper.format_version,
                    parameters.algorithm,
                    parameters.n,
                    parameters.r,
                    parameters.p,
                    wrapper.kdf_salt,
                    "aes-256-gcm",
                    wrapper.nonce,
                    wrapper.ciphertext,
                    wrapper.format_version,
                    _timestamp(),
                    vault_id,
                ),
            )
            if cursor.rowcount != 1:
                raise DatabaseError("master wrapper does not exist")

    def insert_entry(
        self,
        entry_id: str,
        vault_id: bytes,
        payload: EncryptedPayload,
    ) -> None:
        """Insert an already-encrypted payload atomically."""

        _require_entry_id(entry_id)
        _require_bytes(vault_id, "vault_id")
        if not isinstance(payload, EncryptedPayload):
            raise DatabaseError("payload must be an EncryptedPayload")
        now = _timestamp()
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO entries(
                    id, vault_id, record_version, nonce, ciphertext, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (entry_id, vault_id, payload.format_version, payload.nonce, payload.ciphertext, now, now),
            )

    def get_entry(self, entry_id: str) -> EncryptedPayload | None:
        _require_entry_id(entry_id)
        row = self._connection.execute(
            "SELECT record_version, nonce, ciphertext FROM entries WHERE id = ?",
            (entry_id,),
        ).fetchone()
        if row is None:
            return None
        return EncryptedPayload(
            nonce=bytes(row["nonce"]),
            ciphertext=bytes(row["ciphertext"]),
            format_version=row["record_version"],
        )

    def list_entries(self, vault_id: bytes) -> list[tuple[str, EncryptedPayload]]:
        """Return encrypted entry payloads belonging to one vault."""

        _require_bytes(vault_id, "vault_id")
        rows = self._connection.execute(
            """
            SELECT id, record_version, nonce, ciphertext
            FROM entries
            WHERE vault_id = ?
            ORDER BY id
            """,
            (vault_id,),
        ).fetchall()
        return [
            (
                row["id"],
                EncryptedPayload(
                    nonce=bytes(row["nonce"]),
                    ciphertext=bytes(row["ciphertext"]),
                    format_version=row["record_version"],
                ),
            )
            for row in rows
        ]

    def update_entry(
        self,
        entry_id: str,
        vault_id: bytes,
        payload: EncryptedPayload,
    ) -> None:
        _require_entry_id(entry_id)
        _require_bytes(vault_id, "vault_id")
        if not isinstance(payload, EncryptedPayload):
            raise DatabaseError("payload must be an EncryptedPayload")
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE entries
                SET record_version = ?, nonce = ?, ciphertext = ?, updated_at = ?
                WHERE id = ? AND vault_id = ?
                """,
                (
                    payload.format_version,
                    payload.nonce,
                    payload.ciphertext,
                    _timestamp(),
                    entry_id,
                    vault_id,
                ),
            )
            if cursor.rowcount != 1:
                raise DatabaseError("entry does not exist in the selected vault")

    def delete_entry(self, entry_id: str, vault_id: bytes) -> bool:
        _require_entry_id(entry_id)
        _require_bytes(vault_id, "vault_id")
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM entries WHERE id = ? AND vault_id = ?",
                (entry_id, vault_id),
            )
        return cursor.rowcount == 1

    def count_entries(self) -> int:
        return self._connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
