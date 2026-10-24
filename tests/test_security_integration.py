"""End-to-end tests for the security-core boundaries."""

import pytest

from app.security.aead import decrypt_bytes, encrypt_bytes
from app.security.vault_service import AuthenticationError, LocalVaultService
from app.storage.sqlite import VaultDatabase


OLD_PASSWORD = "Strong Master!9"
NEW_PASSWORD = "New Strong Password!7"
ENTRY_ID = "entry-integration-001"


def test_unlocked_session_can_round_trip_an_encrypted_entry():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(OLD_PASSWORD)
    session = service.login(OLD_PASSWORD)
    aad = f"lockbox|v1|record|{ENTRY_ID}".encode("ascii")
    plaintext = b'{"app_name":"Synthetic App","username":"test-user","password":"Synthetic!9"}'

    payload = encrypt_bytes(session.vault_key.material, plaintext, aad)
    database.insert_entry(ENTRY_ID, setup.vault_id, payload)
    stored = database.get_entry(ENTRY_ID)

    assert stored is not None
    assert decrypt_bytes(session.vault_key.material, stored, aad) == plaintext
    database.close()


def test_recovery_reset_preserves_the_vault_key_for_existing_entries():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(OLD_PASSWORD)
    old_session = service.login(OLD_PASSWORD)
    aad = b"lockbox|v1|record|entry-001"
    payload = encrypt_bytes(old_session.vault_key.material, b"existing encrypted entry", aad)
    database.insert_entry("entry-001", setup.vault_id, payload)

    new_session = service.reset_master_password(setup.recovery_key, NEW_PASSWORD)
    stored = database.get_entry("entry-001")

    assert stored is not None
    assert new_session.vault_key.material == old_session.vault_key.material
    assert decrypt_bytes(new_session.vault_key.material, stored, aad) == b"existing encrypted entry"
    database.close()


def test_plaintext_credentials_and_authentication_secrets_are_not_in_storage_columns():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(OLD_PASSWORD)
    session = service.login(OLD_PASSWORD)
    recovery_key = setup.recovery_key
    plaintext = b'{"app_name":"Synthetic App","username":"test-user","password":"Synthetic!9"}'
    payload = encrypt_bytes(session.vault_key.material, plaintext, b"lockbox|v1|record|entry-002")
    database.insert_entry("entry-002", setup.vault_id, payload)

    rows = database.connection.execute(
        "SELECT purpose, kdf_algorithm, encryption_algorithm, wrapped_key FROM key_wrappers "
        "UNION ALL SELECT id, record_version, nonce, ciphertext FROM entries"
    ).fetchall()
    serialized = repr([tuple(row) for row in rows]).encode("utf-8")

    assert OLD_PASSWORD.encode("utf-8") not in serialized
    assert recovery_key.encode("utf-8") not in serialized
    assert plaintext not in serialized
    database.close()


def test_failed_login_does_not_create_an_unlocked_session():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(OLD_PASSWORD)

    with pytest.raises(AuthenticationError):
        service.login("Wrong Password!9")
    database.close()
