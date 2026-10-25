"""Advisory password-strength feedback without retaining password text."""

from dataclasses import dataclass


MINIMUM_PASSWORD_LENGTH = 8
STRENGTH_LABELS = (
    "Very weak",
    "Weak",
    "Fair",
    "Strong",
    "Very strong",
)
COMMON_PASSWORDS = frozenset(
    {
        "12345678",
        "123456789",
        "password",
        "password1",
        "password!",
        "qwerty123",
        "letmein",
        "welcome1",
    }
)


class PasswordStrengthError(ValueError):
    """Raised when strength evaluation receives a non-text password."""


@dataclass(frozen=True, slots=True)
class PasswordStrength:
    """Password-strength result that contains no copy of the password."""

    score: int
    label: str
    meets_policy: bool
    feedback: tuple[str, ...]


def _has_repeated_character_run(password: str) -> bool:
    return any(password[index] == password[index + 1] == password[index + 2] for index in range(len(password) - 2))


def _has_sequential_run(password: str) -> bool:
    lowered = password.casefold()
    sequences = ("0123456789", "abcdefghijklmnopqrstuvwxyz")
    for sequence in sequences:
        for index in range(len(sequence) - 2):
            fragment = sequence[index : index + 3]
            if fragment in lowered or fragment[::-1] in lowered:
                return True
    return False


def evaluate_password(password: str) -> PasswordStrength:
    """Return deterministic, advisory strength feedback for ``password``.

    This is a user-interface aid, not a cryptographic proof of password
    quality. The result intentionally excludes the original password so it can
    be passed between UI components without duplicating secret material.
    """

    if not isinstance(password, str):
        raise PasswordStrengthError("password must be text")

    normalized = password.casefold()
    has_uppercase = any(character.isupper() for character in password)
    has_lowercase = any(character.islower() for character in password)
    has_number = any(character.isdigit() for character in password)
    has_special = any(not character.isalnum() for character in password)
    meets_policy = (
        len(password) >= MINIMUM_PASSWORD_LENGTH
        and has_uppercase
        and has_lowercase
        and has_number
        and has_special
    )

    feedback: list[str] = []
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        feedback.append(f"Use at least {MINIMUM_PASSWORD_LENGTH} characters.")
    elif len(password) < 12:
        feedback.append("Use 12 or more characters for better protection.")
    elif len(password) < 16:
        feedback.append("Use 16 or more characters for stronger protection.")

    if not has_uppercase:
        feedback.append("Add an uppercase letter.")
    if not has_lowercase:
        feedback.append("Add a lowercase letter.")
    if not has_number:
        feedback.append("Add a number.")
    if not has_special:
        feedback.append("Add a special character.")

    is_common = normalized in COMMON_PASSWORDS
    has_repeated_run = _has_repeated_character_run(password)
    has_sequence = _has_sequential_run(password)
    if is_common:
        feedback.append("Avoid common passwords and recognizable words.")
    if has_repeated_run:
        feedback.append("Avoid repeating the same character several times.")
    if has_sequence:
        feedback.append("Avoid predictable letter or number sequences.")

    length_points = min(4, len(password) // 4)
    category_points = sum((has_uppercase, has_lowercase, has_number, has_special))
    score = min(4, length_points + (1 if category_points == 4 else 0))
    if category_points <= 1:
        score = min(score, 1)
    elif category_points == 2:
        score = min(score, 2)
    if is_common:
        score = 0
    elif has_repeated_run or has_sequence:
        score = max(0, score - 1)

    if not feedback:
        feedback.append("Good length and character variety.")
    return PasswordStrength(score, STRENGTH_LABELS[score], meets_policy, tuple(feedback))
