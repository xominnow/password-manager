"""Tests for recovery-key master-password reset."""

import pytest

from app.security.vault_service import (
    AuthenticationError,
    LocalVaultService,
    PasswordPolicyError,
    RecoveryAuthenticationError,
)
from app.storage.sqlite import VaultDatabase


OLD_PASSWORD = "Strong Master!9"
NEW_PASSWORD = "New Strong Password!7"


def test_recovery_reset_replaces_only_the_master_wrapper():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(OLD_PASSWORD)
    before_recovery = bytes(database.get_wrapper("recovery")["wrapped_key"])
    before_master = bytes(database.get_wrapper("master")["wrapped_key"])

    session = service.reset_master_password(setup.recovery_key, NEW_PASSWORD)

    assert session.is_unlocked is True
    assert bytes(database.get_wrapper("recovery")["wrapped_key"]) == before_recovery
    assert bytes(database.get_wrapper("master")["wrapped_key"]) != before_master
    with pytest.raises(AuthenticationError):
        service.login(OLD_PASSWORD)
    assert service.login(NEW_PASSWORD).is_unlocked is True
    database.close()


def test_wrong_recovery_key_does_not_change_master_access():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(OLD_PASSWORD)
    before_master = bytes(database.get_wrapper("master")["wrapped_key"])

    with pytest.raises(RecoveryAuthenticationError):
        service.reset_master_password("AAAA-AAAA-AAAA-AAAA", NEW_PASSWORD)

    assert bytes(database.get_wrapper("master")["wrapped_key"]) == before_master
    assert service.login(OLD_PASSWORD).is_unlocked is True
    database.close()


def test_recovery_reset_validates_new_password_before_replacing_wrapper():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    setup = service.setup(OLD_PASSWORD)
    before_master = bytes(database.get_wrapper("master")["wrapped_key"])

    with pytest.raises(PasswordPolicyError):
        service.reset_master_password(setup.recovery_key, "weak")

    assert bytes(database.get_wrapper("master")["wrapped_key"]) == before_master
    assert service.login(OLD_PASSWORD).is_unlocked is True
    database.close()
