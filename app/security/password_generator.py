"""Cryptographically secure password generation for credential entries."""

import secrets
import string


MINIMUM_GENERATED_LENGTH = 8
UPPERCASE_CHARACTERS = string.ascii_uppercase
LOWERCASE_CHARACTERS = string.ascii_lowercase
NUMBER_CHARACTERS = string.digits
SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{};:,.?/"
ALL_CHARACTERS = (
    UPPERCASE_CHARACTERS
    + LOWERCASE_CHARACTERS
    + NUMBER_CHARACTERS
    + SPECIAL_CHARACTERS
)


class PasswordGenerationError(ValueError):
    """Raised when a requested generated-password length is invalid."""


def generate_password(length: int = 20) -> str:
    """Generate a password containing every required character category.

    ``secrets.choice`` and ``secrets.SystemRandom`` use the operating
    system's cryptographically secure random source. Four characters are
    selected first to guarantee the minimum policy; remaining characters are
    sampled from the complete alphabet and the final sequence is shuffled.
    """

    if isinstance(length, bool) or not isinstance(length, int):
        raise PasswordGenerationError("length must be an integer")
    if length < MINIMUM_GENERATED_LENGTH:
        raise PasswordGenerationError(
            f"length must be at least {MINIMUM_GENERATED_LENGTH} characters"
        )

    required = [
        secrets.choice(UPPERCASE_CHARACTERS),
        secrets.choice(LOWERCASE_CHARACTERS),
        secrets.choice(NUMBER_CHARACTERS),
        secrets.choice(SPECIAL_CHARACTERS),
    ]
    generated = required + [
        secrets.choice(ALL_CHARACTERS) for _ in range(length - len(required))
    ]
    secrets.SystemRandom().shuffle(generated)
    return "".join(generated)
