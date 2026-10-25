"""Regression checks for setup confirmation, secret cleanup and form scrolling."""

import pytest
from kivy.clock import Clock
from kivy.uix.screenmanager import NoTransition

from app.ui.controller import VaultUiController
from app.ui.navigation import Routes, build_app_shell


class FakeClipboard:
    value = ""

    def copy(self, text):
        self.value = text

    def paste(self):
        return self.value

    def clear(self):
        self.value = ""


@pytest.fixture
def shell():
    controller = VaultUiController(":memory:", FakeClipboard())
    manager = build_app_shell(controller)
    manager.transition = NoTransition()
    yield controller, manager
    controller.close()


def test_setup_requires_saved_key_confirmation_and_then_clears_secrets(shell):
    _, manager = shell
    setup = manager.get_screen(Routes.SETUP)
    setup.master.text = setup.confirm.text = "Regression Master!729"
    setup.create_vault()
    assert len(setup.recovery_key) == 16
    assert setup.master.text == setup.confirm.text == ""
    setup.go_to(Routes.LOGIN)
    assert manager.current == Routes.SETUP
    setup.confirm_saved()
    assert manager.current == Routes.LOGIN
    assert setup.recovery_key == setup.recovery_label.text == ""
    assert setup.copy_recovery_button.disabled


@pytest.mark.parametrize("automatic", [False, True])
def test_lock_clears_hidden_screen_values_and_visible_password(shell, automatic):
    controller, manager = shell
    controller.setup("Regression Master!729")
    controller.login("Regression Master!729")
    entry = controller.create("Dummy app", "dummy-user", "DummyPassword!729")
    manager.current = Routes.VAULT
    controller.current_entry_id = entry.entry_id
    manager.current = Routes.DETAIL
    detail = manager.get_screen(Routes.DETAIL)
    detail.toggle_password()
    assert detail.password.text == "DummyPassword!729"
    setup = manager.get_screen(Routes.SETUP)
    setup.recovery_key = "SyntheticOnly123"
    new_master = manager.get_screen(Routes.NEW_MASTER)
    new_master.recovery_key = "SyntheticOnly456"
    draft = manager.get_screen(Routes.ENTRY)
    draft.password.text = "UnsavedPassword!729"
    if automatic:
        controller.auto_lock._clock = lambda: controller.auto_lock._last_activity + 121
        assert controller.check_auto_lock()
    else:
        controller.lock()
    assert not controller.is_unlocked
    assert setup.recovery_key == new_master.recovery_key == draft.password.text == ""
    assert detail.password.text == "••••••••"
    assert manager.get_screen(Routes.VAULT).entries.children == []


def test_generator_round_trip_preserves_draft_and_clears_generated_value(shell):
    controller, manager = shell
    controller.setup("Regression Master!729")
    controller.login("Regression Master!729")
    manager.current = Routes.ENTRY
    entry = manager.get_screen(Routes.ENTRY)
    entry.app_name.text = "Draft App"
    entry.username.text = "draft-user"
    entry.open_generator()
    generator = manager.get_screen(Routes.GENERATOR)
    generated = generator.generated.text
    assert generated
    generator.use_password()
    assert manager.current == Routes.ENTRY
    assert entry.app_name.text == "Draft App"
    assert entry.username.text == "draft-user"
    assert entry.password.text == generated
    assert generator.generated.text == ""
    entry.go_to(Routes.VAULT)
    assert entry.password.text == ""


def test_form_content_grows_and_scrolls_in_short_viewport(shell):
    _, manager = shell
    manager.current = Routes.ENTRY
    manager.size = (360, 240)
    entry = manager.get_screen(Routes.ENTRY)
    for _ in range(5):
        Clock.tick()
    before = entry.root_layout.height
    entry.strength.text = "Long feedback for enlarged fonts. " * 20
    entry.strength.font_size *= 1.5
    for _ in range(5):
        Clock.tick()
    assert entry.root_layout.height > before
    assert entry.root_layout.height > entry.scroll.height
    assert entry.root_layout.size_hint_y is None
