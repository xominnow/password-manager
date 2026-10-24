"""Tests for authenticated, explicitly revealed password copying."""

import pytest

from app.platform.clipboard import ClipboardError, ClipboardService
from app.security.vault_service import LocalVaultService
from app.services.credentials import CredentialService
from app.storage.sqlite import VaultDatabase


MASTER_PASSWORD = "Strong Master!9"


class FakeClipboard:
    def __init__(self):
        self.value = ""

    def copy(self, text):
        self.value = text

    def paste(self):
        return self.value

    def clear(self):
        self.value = ""


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def __call__(self):
        return self.value


def _credential_view():
    database = VaultDatabase(":memory:")
    service = LocalVaultService(database)
    service.setup(MASTER_PASSWORD)
    session = service.login(MASTER_PASSWORD)
    record = CredentialService(database).create(
        session,
        "Example App",
        "demo-user",
        "Synthetic!9",
    )
    view = CredentialService(database).view(session, record.entry_id)
    assert view is not None
    return database, session, view


def test_copy_requires_revealed_password_and_copies_only_password():
    database, session, view = _credential_view()
    clipboard = FakeClipboard()
    service = ClipboardService(clipboard)

    with pytest.raises(ClipboardError):
        service.copy_password(session, view)

    service.copy_password(session, view.reveal())
    assert clipboard.paste() == "Synthetic!9"
    assert "Example App" not in clipboard.paste()
    assert "demo-user" not in clipboard.paste()
    database.close()


def test_explicit_recovery_key_copy_uses_clipboard_timeout():
    clipboard = FakeClipboard()
    clock = FakeClock()
    service = ClipboardService(clipboard, clock=clock)

    service.copy_recovery_key("Ab12Cd34Ef56Gh78")
    assert clipboard.paste() == "Ab12Cd34Ef56Gh78"
    clock.value = 30.0
    assert service.clear_expired() is True
    assert clipboard.paste() == ""


def test_copy_rejects_locked_session_and_invalid_view():
    database, session, view = _credential_view()
    service = ClipboardService(FakeClipboard())
    session.lock()

    with pytest.raises(ClipboardError):
        service.copy_password(session, view.reveal())
    with pytest.raises(ClipboardError):
        service.copy_password(session, object())
    database.close()


def test_clipboard_adapter_contract_can_clear_values():
    clipboard = FakeClipboard()
    clipboard.copy("Synthetic!9")
    assert clipboard.paste() == "Synthetic!9"
    clipboard.clear()
    assert clipboard.paste() == ""


def test_expired_app_owned_clipboard_value_is_cleared_at_30_seconds():
    database, session, view = _credential_view()
    clipboard = FakeClipboard()
    clock = FakeClock()
    service = ClipboardService(clipboard, clock=clock)

    service.copy_password(session, view.reveal())
    clock.value = 29.99
    assert service.clear_expired() is False
    assert clipboard.paste() == "Synthetic!9"
    clock.value = 30.0
    assert service.clear_expired() is True
    assert clipboard.paste() == ""
    assert service.clear_expired() is False
    database.close()


def test_timeout_does_not_overwrite_newer_clipboard_value():
    database, session, view = _credential_view()
    clipboard = FakeClipboard()
    clock = FakeClock()
    service = ClipboardService(clipboard, clock=clock)

    service.copy_password(session, view.reveal())
    clipboard.copy("Copied by another app")
    clock.value = 30.0
    assert service.clear_expired() is False
    assert clipboard.paste() == "Copied by another app"
    database.close()


def test_copying_again_resets_clipboard_timeout():
    database, session, view = _credential_view()
    clipboard = FakeClipboard()
    clock = FakeClock()
    service = ClipboardService(clipboard, clock=clock)

    service.copy_password(session, view.reveal())
    clock.value = 25.0
    service.copy_password(session, view.reveal())
    clock.value = 54.99
    assert service.clear_expired() is False
    assert clipboard.paste() == "Synthetic!9"
    clock.value = 55.0
    assert service.clear_expired() is True
    database.close()
