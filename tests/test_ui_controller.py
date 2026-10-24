"""Integration tests for the service-connected UI controller."""

import pytest

from app.ui.controller import UiControllerError, VaultUiController


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


def test_ui_controller_connects_vault_crud_search_generation_and_clipboard():
    clipboard = FakeClipboard()
    controller = VaultUiController(":memory:", clipboard)

    assert controller.has_vault is False
    recovery_key = controller.setup(MASTER_PASSWORD)
    assert recovery_key
    controller.login(MASTER_PASSWORD)

    record = controller.create("Example App", "demo-user", "Synthetic!9")
    assert [item.app_name for item in controller.search("example")] == ["Example App"]
    view = controller.view(record.entry_id)
    assert view is not None
    assert view.displayed_password == "••••••••"
    controller.reveal_current()
    controller.copy_current_password()
    assert clipboard.value == "Synthetic!9"

    generated = controller.generate_password()
    assert controller.password_strength(generated).meets_policy is True
    controller.update(record.entry_id, "Updated App", "updated-user", generated)
    assert controller.search("UPDATED")[0].username == "updated-user"
    assert controller.delete(record.entry_id) is True
    assert controller.search() == ()
    controller.close()


def test_ui_controller_lock_rejects_subsequent_sensitive_actions():
    controller = VaultUiController(":memory:", FakeClipboard())
    controller.setup(MASTER_PASSWORD)
    controller.login(MASTER_PASSWORD)
    controller.lock()

    with pytest.raises(UiControllerError):
        controller.search()
    with pytest.raises(UiControllerError):
        controller.create("Example App", "user", "Password!9")
    controller.close()
