"""R-01: explicit visibility controls and safe reset for every password input."""

import pytest
from kivy.clock import Clock
from kivy.uix.screenmanager import NoTransition

from app.platform.clipboard import ClipboardError
from app.ui.controller import VaultUiController
from app.ui.navigation import Routes, build_app_shell
from app.ui.screens import BODY_FONT_SIZE


MASTER = "Synthetic Master!729"
PASSWORD_FIELDS = (
    (Routes.SETUP, "master", "master password"),
    (Routes.SETUP, "confirm", "confirmation"),
    (Routes.LOGIN, "master", "master password"),
    (Routes.NEW_MASTER, "master", "new master password"),
    (Routes.NEW_MASTER, "confirm", "confirmation"),
    (Routes.ENTRY, "password", "password"),
)
PASSWORD_ROUTES = (Routes.SETUP, Routes.LOGIN, Routes.NEW_MASTER, Routes.ENTRY)


class FakeClipboard:
    def __init__(self):
        self.value = ""
        self.copy_calls = 0

    def copy(self, text):
        self.value = text
        self.copy_calls += 1

    def paste(self):
        return self.value

    def clear(self):
        self.value = ""


@pytest.fixture
def shell():
    clipboard = FakeClipboard()
    controller = VaultUiController(":memory:", clipboard)
    manager = build_app_shell(controller)
    manager.transition = NoTransition()
    yield controller, manager, clipboard
    controller.close()


@pytest.mark.parametrize("route,attribute,label", PASSWORD_FIELDS)
def test_each_password_input_has_an_independent_explicit_toggle(shell, route, attribute, label):
    controller, manager, clipboard = shell
    screen = manager.get_screen(route)
    field = getattr(screen, attribute)
    toggle = screen._password_toggles[field]
    assert field.password is True
    assert toggle.text == f"Show {label}"
    assert toggle.font_size == BODY_FONT_SIZE
    assert toggle.parent is field.parent is screen.root_layout
    field.text = "Synthetic-only!7"

    toggle.dispatch("on_release")
    assert field.password is False
    assert field.text == "Synthetic-only!7"
    assert toggle.text == f"Hide {label}"
    assert all(other.password for other in screen._password_toggles if other is not field)
    field.text += "x"
    assert field.password is False
    toggle.dispatch("on_release")
    assert field.password is True
    assert field.text == "Synthetic-only!7x"
    assert toggle.text == f"Show {label}"
    assert not controller.has_vault
    assert not controller.is_unlocked
    assert clipboard.copy_calls == 0
    assert clipboard.value == ""


@pytest.mark.parametrize("route", PASSWORD_ROUTES)
def test_sensitive_cleanup_resets_masking_and_button_labels(shell, route):
    _, manager, _ = shell
    screen = manager.get_screen(route)
    for field, toggle in screen._password_toggles.items():
        field.text = "Synthetic-only!7"
        toggle.dispatch("on_release")
    screen.clear_sensitive()
    for field, toggle in screen._password_toggles.items():
        assert field.text == ""
        assert field.password is True
        assert toggle.text.startswith("Show ")


@pytest.mark.parametrize("route", PASSWORD_ROUTES)
def test_screen_navigation_clears_and_remasks_inputs(shell, route):
    _, manager, _ = shell
    manager.current = route
    screen = manager.get_screen(route)
    for field, toggle in screen._password_toggles.items():
        field.text = "Synthetic-only!7"
        toggle.dispatch("on_release")
    screen.go_to(Routes.RECOVERY)
    assert manager.current == Routes.RECOVERY
    for field, toggle in screen._password_toggles.items():
        assert field.text == ""
        assert field.password is True
        assert toggle.text.startswith("Show ")


@pytest.mark.parametrize("automatic", [False, True])
def test_manual_and_automatic_lock_remask_even_inactive_inputs(shell, automatic):
    controller, manager, clipboard = shell
    controller.setup(MASTER)
    controller.login(MASTER)
    manager.current = Routes.ENTRY
    for route, attribute, _ in PASSWORD_FIELDS:
        screen = manager.get_screen(route)
        field = getattr(screen, attribute)
        field.text = "Synthetic-only!7"
        screen._password_toggles[field].dispatch("on_release")
    if automatic:
        controller.auto_lock._clock = lambda: controller.auto_lock._last_activity + 121
        assert controller.check_auto_lock()
    else:
        controller.lock()
    assert not controller.is_unlocked
    for route, attribute, _ in PASSWORD_FIELDS:
        screen = manager.get_screen(route)
        field = getattr(screen, attribute)
        assert field.password is True
        assert field.text == ""
        assert screen._password_toggles[field].text.startswith("Show ")
    assert clipboard.copy_calls == 0


@pytest.mark.parametrize("apply_generated", [False, True])
def test_generator_keeps_the_draft_but_does_not_keep_it_revealed(shell, apply_generated):
    controller, manager, _ = shell
    controller.setup(MASTER)
    controller.login(MASTER)
    manager.current = Routes.ENTRY
    entry = manager.get_screen(Routes.ENTRY)
    entry.app_name.text = "Synthetic draft"
    entry.username.text = "dummy-user"
    entry.password.text = "Synthetic-only!7"
    toggle = entry._password_toggles[entry.password]
    toggle.dispatch("on_release")
    entry.open_generator()
    assert entry.password.text == "Synthetic-only!7"
    assert entry.password.password is True
    assert toggle.text == "Show password"
    generator = manager.get_screen(Routes.GENERATOR)
    generated = generator.generated.text
    if apply_generated:
        generator.use_password()
    else:
        generator.go_to(Routes.ENTRY)
    assert entry.password.text == (generated if apply_generated else "Synthetic-only!7")
    assert entry.password.password is True
    assert toggle.text == "Show password"
    assert entry.app_name.text == "Synthetic draft"
    assert entry.username.text == "dummy-user"


def test_successful_setup_remasks_both_fields_before_key_acknowledgement(shell):
    controller, manager, clipboard = shell
    setup = manager.get_screen(Routes.SETUP)
    setup.master.text = setup.confirm.text = MASTER
    for toggle in setup._password_toggles.values():
        toggle.dispatch("on_release")
    setup.create_vault()
    assert controller.has_vault
    assert len(setup.recovery_key) == 16
    assert not setup.recovery_saved
    for field, toggle in setup._password_toggles.items():
        assert field.password is True
        assert field.text == ""
        assert toggle.text.startswith("Show ")
    assert clipboard.copy_calls == 0


def test_visibility_toggle_counts_as_activity_without_changing_lock_duration(shell):
    controller, manager, _ = shell
    controller.setup(MASTER)
    controller.login(MASTER)
    manager.current = Routes.ENTRY
    now = [controller.auto_lock._last_activity + 110]
    controller.auto_lock._clock = lambda: now[0]
    entry = manager.get_screen(Routes.ENTRY)
    entry._password_toggles[entry.password].dispatch("on_release")
    assert controller.auto_lock._last_activity == now[0]
    now[0] += 119
    assert not controller.check_auto_lock()
    now[0] += 1
    assert controller.check_auto_lock()
    assert entry.password.password is True


def test_edit_visibility_does_not_reveal_detail_or_change_saved_record(shell):
    controller, manager, clipboard = shell
    controller.setup(MASTER)
    controller.login(MASTER)
    record = controller.create("Synthetic app", "dummy-user", "Synthetic-only!7")
    controller.current_entry_id = record.entry_id
    manager.current = Routes.DETAIL
    detail = manager.get_screen(Routes.DETAIL)
    detail.edit_entry()
    entry = manager.get_screen(Routes.ENTRY)
    assert entry.password.text == "Synthetic-only!7"
    assert entry.password.password is True
    entry._password_toggles[entry.password].dispatch("on_release")
    assert entry.password.password is False
    assert not controller.current_view.password_visible
    assert controller.current_view.displayed_password == "••••••••"
    with pytest.raises(ClipboardError):
        controller.copy_current_password()
    assert controller.view(record.entry_id).reveal().displayed_password == "Synthetic-only!7"
    assert clipboard.copy_calls == 0


@pytest.mark.parametrize("route", PASSWORD_ROUTES)
def test_password_controls_remain_in_scrollable_enlarged_font_forms(shell, route):
    _, manager, _ = shell
    manager.current = route
    manager.size = (360, 240)
    screen = manager.get_screen(route)
    for toggle in screen._password_toggles.values():
        toggle.font_size *= 1.5
    for _ in range(5):
        Clock.tick()
    assert screen.root_layout.height > screen.scroll.height
    for toggle in screen._password_toggles.values():
        assert toggle.text_size[0] > 0
        assert toggle.height >= toggle.texture_size[1]
