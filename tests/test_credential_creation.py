"""Tests for encrypted credential creation."""

import json

import pytest

from app.security.aead import decrypt_bytes
from app.security.vault_service import LocalVaultService
from app.services.credentials import (
    CredentialService,
    CredentialValidationError,
    entry_associated_data,
)
from app.storage.sqlite import VaultDatabase


PASSWORD = "Strong Master!9"


def test_create_encrypts_and_stores_a_credential_record():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(PASSWORD)
    session = service.login(PASSWORD)

    record = CredentialService(database).create(
        session,
        "Example App",
        "demo-user",
        "Synthetic!9",
    )
    stored = database.get_entry(record.entry_id)

    assert stored is not None
    assert database.count_entries() == 1
    plaintext = decrypt_bytes(
        session.vault_key.material,
        stored,
        entry_associated_data(setup.vault_id, record.entry_id),
    )
    assert json.loads(plaintext) == {
        "app_name": "Example App",
        "password": "Synthetic!9",
        "username": "demo-user",
    }
    database.close()


def test_creation_rejects_locked_sessions_and_incomplete_fields():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(PASSWORD)
    session = service.login(PASSWORD)
    credential_service = CredentialService(database)
    session.lock()

    with pytest.raises(CredentialValidationError):
        credential_service.create(session, "Example App", "user", "password")
    with pytest.raises(CredentialValidationError):
        credential_service.create(session, "", "user", "password")
    database.close()


def test_database_does_not_contain_plaintext_credential_fields():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(PASSWORD)
    session = service.login(PASSWORD)
    CredentialService(database).create(session, "Example App", "demo-user", "Synthetic!9")

    columns = {row["name"] for row in database.connection.execute("PRAGMA table_info(entries)")}
    assert {"app_name", "username", "password"}.isdisjoint(columns)
    database.close()
