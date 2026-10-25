"""Tests for centralized application defaults."""

import pytest

from app.config import DEFAULT_SETTINGS


def test_security_defaults_match_approved_requirements():
    assert DEFAULT_SETTINGS.auto_lock_seconds == 120
    assert DEFAULT_SETTINGS.minimum_password_length == 8
    assert DEFAULT_SETTINGS.require_uppercase is True
    assert DEFAULT_SETTINGS.require_lowercase is True
    assert DEFAULT_SETTINGS.require_number is True
    assert DEFAULT_SETTINGS.require_special_character is True


def test_settings_are_immutable():
    with pytest.raises(AttributeError):
        DEFAULT_SETTINGS.auto_lock_seconds = 60
