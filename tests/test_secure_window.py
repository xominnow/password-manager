"""Tests for secure-window adapter behavior."""

import pytest

from app.platform.secure_window import (
    SecureWindowController,
    SecureWindowError,
    apply_secure_flag,
    apply_secure_flag_on_ui_thread,
)


class FakeWindow:
    def __init__(self):
        self.flags = []

    def addFlags(self, flag):
        self.flags.append(flag)


class FakeActivity:
    def __init__(self):
        self.window = FakeWindow()

    def getWindow(self):
        return self.window


def immediate_runnable(callback):
    """Test double for python-for-android's UI-thread Runnable wrapper."""

    class Runnable:
        def __call__(self):
            callback()

    return Runnable()


class FakeAdapter:
    def __init__(self, error=None):
        self.error = error
        self.calls = 0

    def enable(self):
        self.calls += 1
        if self.error:
            raise self.error


def test_secure_flag_is_applied_to_activity_window():
    activity = FakeActivity()

    apply_secure_flag(activity, 0x2000)

    assert activity.window.flags == [0x2000]


def test_secure_flag_rejects_unavailable_activity():
    with pytest.raises(SecureWindowError):
        apply_secure_flag(None, 0x2000)


def test_secure_flag_ui_thread_boundary_applies_flag():
    activity = FakeActivity()

    apply_secure_flag_on_ui_thread(activity, 0x2000, immediate_runnable)

    assert activity.window.flags == [0x2000]


def test_secure_flag_ui_thread_boundary_fails_when_callback_errors():
    with pytest.raises(SecureWindowError, match="could not be enabled"):
        apply_secure_flag_on_ui_thread(None, 0x2000, immediate_runnable)


def test_controller_records_enablement_only_after_success():
    adapter = FakeAdapter()
    controller = SecureWindowController(adapter)

    controller.enable()

    assert controller.enabled is True
    assert adapter.calls == 1


def test_controller_does_not_claim_protection_after_failure():
    adapter = FakeAdapter(SecureWindowError("failed"))
    controller = SecureWindowController(adapter)

    with pytest.raises(SecureWindowError):
        controller.enable()
    assert controller.enabled is False
