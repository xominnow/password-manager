"""Tests for two-minute inactivity auto-lock behavior."""

import pytest

from app.security.vault_service import LocalVaultService
from app.services.session import AutoLockController, SessionControlError
from app.storage.sqlite import VaultDatabase


MASTER_PASSWORD = "Strong Master!9"


class FakeClock:
    def __init__(self):
        self.value = 100.0

    def __call__(self):
        return self.value


def _session():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(MASTER_PASSWORD)
    return database, service.login(MASTER_PASSWORD)


def test_auto_lock_happens_at_120_seconds_of_inactivity():
    database, session = _session()
    clock = FakeClock()
    controller = AutoLockController(session, clock=clock)

    clock.value = 219.99
    assert controller.check_auto_lock() is False
    assert session.is_unlocked is True
    clock.value = 220.0
    assert controller.check_auto_lock() is True
    assert session.is_unlocked is False
    assert controller.check_auto_lock() is False
    database.close()


def test_qualifying_activity_resets_the_inactivity_deadline():
    database, session = _session()
    clock = FakeClock()
    controller = AutoLockController(session, clock=clock)

    clock.value = 210.0
    assert controller.record_activity() is True
    clock.value = 329.99
    assert controller.check_auto_lock() is False
    clock.value = 330.0
    assert controller.check_auto_lock() is True
    database.close()


def test_manual_lock_is_immediate_and_activity_cannot_unlock_session():
    database, session = _session()
    clock = FakeClock()
    controller = AutoLockController(session, clock=clock)

    controller.lock_now()
    assert session.is_unlocked is False
    assert controller.record_activity() is False
    assert controller.check_auto_lock() is False
    database.close()


@pytest.mark.parametrize("timeout", [0, -1, True, "120"])
def test_controller_rejects_invalid_timeout(timeout):
    database, session = _session()
    with pytest.raises(SessionControlError):
        AutoLockController(session, timeout_seconds=timeout)
    database.close()
