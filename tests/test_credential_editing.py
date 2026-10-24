"""Tests for atomic encrypted credential editing."""

import pytest

from app.security.vault_service import LocalVaultService
from app.services.credentials import (
    CredentialNotFoundError,
    CredentialService,
    CredentialValidationError,
)
from app.storage.sqlite import VaultDatabase


MASTER_PASSWORD = "Strong Master!9"


def _created_credential():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(MASTER_PASSWORD)
    session = service.login(MASTER_PASSWORD)
    credential_service = CredentialService(database)
    record = credential_service.create(
        session,
        "Example App",
        "demo-user",
        "Synthetic!9",
    )
    return database, session, credential_service, record


def test_update_reuses_entry_id_replaces_encrypted_payload_and_is_readable():
    database, session, credential_service, record = _created_credential()
    old_payload = database.get_entry(record.entry_id)
    assert old_payload is not None

    updated = credential_service.update(
        session,
        record.entry_id,
        "Updated App",
        "updated-user",
        "Updated!9",
    )

    new_payload = database.get_entry(record.entry_id)
    assert new_payload is not None
    assert updated.entry_id == record.entry_id
    assert updated.app_name == "Updated App"
    assert updated.username == "updated-user"
    assert old_payload.nonce != new_payload.nonce
    assert old_payload.ciphertext != new_payload.ciphertext

    view = credential_service.view(session, record.entry_id)
    assert view is not None
    assert view.app_name == "Updated App"
    assert view.username == "updated-user"
    assert view.reveal().displayed_password == "Updated!9"
    database.close()


def test_update_rejects_missing_entry_and_locked_session():
    database, session, credential_service, record = _created_credential()

    with pytest.raises(CredentialNotFoundError):
        credential_service.update(
            session,
            "missing-entry",
            "Updated App",
            "updated-user",
            "Updated!9",
        )

    session.lock()
    with pytest.raises(CredentialValidationError):
        credential_service.update(
            session,
            record.entry_id,
            "Updated App",
            "updated-user",
            "Updated!9",
        )
    database.close()


@pytest.mark.parametrize(
    ("app_name", "username", "password"),
    [
        ("", "user", "Password!9"),
        ("App", "", "Password!9"),
        ("App", "user", ""),
    ],
)
def test_update_rejects_invalid_fields(app_name, username, password):
    database, session, credential_service, record = _created_credential()

    with pytest.raises(CredentialValidationError):
        credential_service.update(
            session,
            record.entry_id,
            app_name,
            username,
            password,
        )
    database.close()
