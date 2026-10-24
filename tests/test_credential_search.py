"""Tests for encrypted app/website-name search."""

import pytest

from app.security.vault_service import LocalVaultService
from app.services.credentials import (
    CredentialReadError,
    CredentialService,
    CredentialValidationError,
)
from app.storage.sqlite import VaultDatabase


MASTER_PASSWORD = "Strong Master!9"


def _service_with_credentials():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(MASTER_PASSWORD)
    session = service.login(MASTER_PASSWORD)
    credential_service = CredentialService(database)
    records = [
        credential_service.create(session, "GitHub", "git-user", "Github!9"),
        credential_service.create(session, "Bank Portal", "bank-user", "Banking!9"),
        credential_service.create(session, "GitHub Enterprise", "enterprise-user", "Enterprise!9"),
    ]
    return database, session, credential_service, records


def test_search_matches_app_names_case_insensitively_and_masks_passwords():
    database, session, credential_service, records = _service_with_credentials()

    results = credential_service.search(session, "  GITHUB  ")

    assert [item.app_name for item in results] == ["GitHub", "GitHub Enterprise"]
    assert {item.entry_id for item in results} == {records[0].entry_id, records[2].entry_id}
    assert all(item.displayed_password == "••••••••" for item in results)
    database.close()


def test_empty_search_returns_all_entries_in_deterministic_order():
    database, session, credential_service, _ = _service_with_credentials()

    results = credential_service.search(session)

    assert [item.app_name for item in results] == [
        "Bank Portal",
        "GitHub",
        "GitHub Enterprise",
    ]
    database.close()


def test_search_rejects_locked_or_non_text_queries():
    database, session, credential_service, _ = _service_with_credentials()

    with pytest.raises(CredentialValidationError):
        credential_service.search(session, 123)
    session.lock()
    with pytest.raises(CredentialValidationError):
        credential_service.search(session, "GitHub")
    database.close()


def test_search_rejects_tampered_payloads():
    database, session, credential_service, records = _service_with_credentials()
    stored = database.get_entry(records[0].entry_id)
    assert stored is not None
    database.connection.execute(
        "UPDATE entries SET ciphertext = ? WHERE id = ?",
        (stored.ciphertext[:-1] + bytes([stored.ciphertext[-1] ^ 1]), records[0].entry_id),
    )
    database.connection.commit()

    with pytest.raises(CredentialReadError):
        credential_service.search(session)
    database.close()
