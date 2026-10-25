"""Tests for master-password setup and login."""

import pytest

from app.security.vault_service import (
    AuthenticationError,
    LocalVaultService,
    PasswordPolicyError,
    VaultAlreadyInitialized,
    VaultNotInitialized,
)
from app.storage.sqlite import VaultDatabase


PASSWORD = "Strong Master!9"


def test_setup_creates_local_vault_and_returns_recovery_key_once():
    database = VaultDatabase(":memory:")
    result = LocalVaultService(database).setup(PASSWORD)

    assert len(result.vault_id) == 16
    assert len(result.recovery_key) == 16
    assert result.recovery_key.isalnum()
    assert database.get_vault_id() == result.vault_id
    assert database.get_wrapper("master") is not None
    assert database.get_wrapper("recovery") is not None
    database.close()


def test_login_unlocks_and_lock_clears_session_key():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(PASSWORD)

    session = service.login(PASSWORD)
    assert session.is_unlocked is True
    assert session.vault_id == setup.vault_id
    assert len(session.vault_key.material) == 32
    session.lock()
    assert session.is_unlocked is False
    with pytest.raises(ValueError):
        _ = session.vault_key
    database.close()


def test_wrong_password_and_repeated_setup_are_rejected():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(PASSWORD)

    with pytest.raises(AuthenticationError):
        service.login("Wrong Password!9")
    with pytest.raises(VaultAlreadyInitialized):
        service.setup(PASSWORD)
    database.close()


def test_login_before_setup_and_weak_password_are_rejected():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)

    with pytest.raises(VaultNotInitialized):
        service.login(PASSWORD)
    with pytest.raises(PasswordPolicyError):
        service.setup("weak")
    database.close()
