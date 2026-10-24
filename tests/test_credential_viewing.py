"""Tests for authenticated credential viewing and password masking."""

from dataclasses import replace

import pytest

from app.security.vault_service import LocalVaultService
from app.services.credentials import (
    CredentialReadError,
    CredentialService,
    CredentialValidationError,
    MASKED_PASSWORD,
)
from app.storage.sqlite import VaultDatabase


PASSWORD = "Strong Master!9"


def _created_credential():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(PASSWORD)
    session = service.login(PASSWORD)
    record = CredentialService(database).create(
        session,
        "Example App",
        "demo-user",
        "Synthetic!9",
    )
    return database, session, record


def test_view_masks_password_until_explicit_reveal():
    database, session, record = _created_credential()
    view = CredentialService(database).view(session, record.entry_id)

    assert view is not None
    assert view.app_name == "Example App"
    assert view.username == "demo-user"
    assert view.password_visible is False
    assert view.displayed_password == MASKED_PASSWORD
    assert view.reveal().displayed_password == "Synthetic!9"
    assert view.reveal().hide().displayed_password == MASKED_PASSWORD
    database.close()


def test_view_returns_none_for_missing_entry_and_rejects_locked_session():
    database, session, record = _created_credential()
    credential_service = CredentialService(database)

    assert credential_service.view(session, "missing-entry") is None
    session.lock()
    with pytest.raises(CredentialValidationError):
        credential_service.view(session, record.entry_id)
    database.close()


def test_view_rejects_tampered_ciphertext_without_displaying_plaintext():
    database, session, record = _created_credential()
    stored = database.get_entry(record.entry_id)
    assert stored is not None
    database.connection.execute(
        "UPDATE entries SET ciphertext = ? WHERE id = ?",
        (stored.ciphertext[:-1] + bytes([stored.ciphertext[-1] ^ 1]), record.entry_id),
    )
    database.connection.commit()

    with pytest.raises(CredentialReadError):
        CredentialService(database).view(session, record.entry_id)
    database.close()
