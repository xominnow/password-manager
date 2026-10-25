"""Tests for encrypted SQLite storage boundaries and transaction behavior."""

import sqlite3

import pytest

from app.security.aead import encrypt_bytes
from app.security.keys import create_vault_key
from app.security.randomness import decode_recovery_key, generate_recovery_key
from app.security.wrapping import wrap_master_key, wrap_recovery_key
from app.storage.sqlite import DatabaseError, VaultDatabase


def _initialized_database():
    vault_id = b"vault-id-0000001"
    vault_context = vault_id.hex()
    vault_key = create_vault_key()
    recovery_key = decode_recovery_key(generate_recovery_key())
    master_wrapper = wrap_master_key(vault_key, "master password", vault_context)
    recovery_wrapper = wrap_recovery_key(vault_key, recovery_key, vault_context)
    database = VaultDatabase(":memory:")
    database.initialize_vault(vault_id, (master_wrapper, recovery_wrapper))
    return database, vault_id


def test_schema_enables_foreign_keys_and_stores_two_wrappers():
    database, _ = _initialized_database()

    assert database.foreign_keys_enabled() is True
    assert {row["purpose"] for row in database.list_wrappers()} == {"master", "recovery"}
    assert database.connection.execute("SELECT COUNT(*) FROM vault_metadata").fetchone()[0] == 1
    database.close()


def test_entries_store_only_encrypted_payload_columns():
    database, vault_id = _initialized_database()
    payload = encrypt_bytes(create_vault_key().material, b"synthetic credential", b"record-aad")

    database.insert_entry("entry-001", vault_id, payload)
    stored = database.get_entry("entry-001")

    assert stored == payload
    columns = {
        row["name"] for row in database.connection.execute("PRAGMA table_info(entries)").fetchall()
    }
    assert {"username", "password", "app_name"}.isdisjoint(columns)
    assert database.count_entries() == 1
    database.close()


def test_entry_update_and_delete_are_scoped_and_atomic():
    database, vault_id = _initialized_database()
    first = encrypt_bytes(create_vault_key().material, b"first", b"record-aad")
    second = encrypt_bytes(create_vault_key().material, b"second", b"record-aad")
    database.insert_entry("entry-001", vault_id, first)
    database.update_entry("entry-001", vault_id, second)
    assert database.get_entry("entry-001") == second
    assert database.delete_entry("entry-001", vault_id) is True
    assert database.get_entry("entry-001") is None
    assert database.delete_entry("entry-001", vault_id) is False
    database.close()


def test_foreign_key_and_duplicate_constraints_prevent_invalid_writes():
    database, vault_id = _initialized_database()
    payload = encrypt_bytes(create_vault_key().material, b"synthetic", b"record-aad")
    database.insert_entry("entry-001", vault_id, payload)

    with pytest.raises(sqlite3.IntegrityError):
        database.insert_entry("entry-001", vault_id, payload)
    with pytest.raises(sqlite3.IntegrityError):
        database.insert_entry("entry-002", b"wrong-vault", payload)
    database.close()


def test_database_rejects_incomplete_vault_initialization():
    database = VaultDatabase(":memory:")

    with pytest.raises(DatabaseError):
        database.initialize_vault(b"vault-id-0000001", ())
    database.close()
