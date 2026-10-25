"""Tests for cryptographically secure password generation."""

import string

import pytest

from app.security.password_generator import (
    MINIMUM_GENERATED_LENGTH,
    PasswordGenerationError,
    generate_password,
)


def test_generated_password_meets_all_required_categories():
    password = generate_password(24)

    assert len(password) == 24
    assert any(character in string.ascii_uppercase for character in password)
    assert any(character in string.ascii_lowercase for character in password)
    assert any(character in string.digits for character in password)
    assert any(not character.isalnum() for character in password)


def test_generated_password_supports_minimum_length_and_varied_lengths():
    minimum = generate_password(MINIMUM_GENERATED_LENGTH)
    longer = generate_password(64)

    assert len(minimum) == MINIMUM_GENERATED_LENGTH
    assert len(longer) == 64


@pytest.mark.parametrize("length", [0, 1, 7, -1, True, "20"])
def test_generator_rejects_invalid_lengths(length):
    with pytest.raises(PasswordGenerationError):
        generate_password(length)


def test_generated_passwords_are_not_repeated_by_design():
    passwords = {generate_password(20) for _ in range(8)}

    assert len(passwords) == 8
