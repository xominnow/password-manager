"""Tests for confirmed, vault-scoped credential deletion."""

import pytest

from app.security.vault_service import LocalVaultService
from app.services.credentials import CredentialService, CredentialValidationError
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


def test_delete_requires_confirmation_and_removes_entry_after_confirmation():
    database, session, credential_service, record = _created_credential()

    with pytest.raises(CredentialValidationError):
        credential_service.delete(session, record.entry_id)
    assert database.get_entry(record.entry_id) is not None

    assert credential_service.delete(session, record.entry_id, confirmed=True) is True
    assert database.get_entry(record.entry_id) is None
    assert credential_service.view(session, record.entry_id) is None
    database.close()


def test_delete_returns_false_for_missing_entry_and_rejects_locked_session():
    database, session, credential_service, record = _created_credential()

    assert credential_service.delete(session, "missing-entry", confirmed=True) is False

    session.lock()
    with pytest.raises(CredentialValidationError):
        credential_service.delete(session, record.entry_id, confirmed=True)
    database.close()


def test_delete_rejects_invalid_entry_id_and_false_confirmation():
    database, session, credential_service, record = _created_credential()

    with pytest.raises(CredentialValidationError):
        credential_service.delete(session, "", confirmed=True)
    with pytest.raises(CredentialValidationError):
        credential_service.delete(session, record.entry_id, confirmed=1)
    database.close()
