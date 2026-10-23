"""Centralized non-secret application configuration.

Security-sensitive values such as the master password, recovery answers,
vault keys, and encryption material must never be stored in this module or in
environment variables. They belong in the encrypted local vault workflow.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Immutable product defaults shared by the UI and application services."""

    app_name: str = "Lockbox"
    auto_lock_seconds: int = 120
    minimum_password_length: int = 8
    generated_password_length: int = 20
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_number: bool = True
    require_special_character: bool = True


DEFAULT_SETTINGS = AppSettings()
