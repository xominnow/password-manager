"""Clipboard adapter and authenticated password-copy service."""

import time
from typing import Callable, Protocol

from kivy.core.clipboard import Clipboard

from app.config import DEFAULT_SETTINGS
from app.security.vault_service import UnlockedVaultSession
from app.services.credentials import CredentialView


class ClipboardError(RuntimeError):
    """Raised when a password cannot be copied safely."""


class ClipboardAdapter(Protocol):
    """Minimal clipboard contract used by the service and test fakes."""

    def copy(self, text: str) -> None:
        """Place text on the platform clipboard."""

    def paste(self) -> str:
        """Read the current platform clipboard value."""

    def clear(self) -> None:
        """Clear the platform clipboard."""


class KivyClipboardAdapter:
    """Android-compatible clipboard adapter backed by Kivy Clipboard."""

    def copy(self, text: str) -> None:
        Clipboard.copy(text)

    def paste(self) -> str:
        return Clipboard.paste()

    def clear(self) -> None:
        Clipboard.copy("")


class ClipboardService:
    """Copy an explicitly revealed password without logging or persistence."""

    def __init__(
        self,
        adapter: ClipboardAdapter,
        *,
        timeout_seconds: int = DEFAULT_SETTINGS.clipboard_timeout_seconds,
        clock: Callable[[], float] = time.monotonic,
    ):
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise ClipboardError("timeout_seconds must be a positive integer")
        if not callable(clock):
            raise ClipboardError("clock must be callable")
        self.adapter = adapter
        self.timeout_seconds = timeout_seconds
        self._clock = clock
        self._copied_value: str | None = None
        self._copied_at: float | None = None

    def copy_password(
        self,
        session: UnlockedVaultSession,
        view: CredentialView,
    ) -> None:
        """Copy only a revealed password for an unlocked authenticated session."""

        if not isinstance(session, UnlockedVaultSession) or not session.is_unlocked:
            raise ClipboardError("vault must be unlocked")
        if not isinstance(view, CredentialView):
            raise ClipboardError("credential view is required")
        if not view.password_visible:
            raise ClipboardError("reveal the password before copying")
        password = view.displayed_password
        if not password:
            raise ClipboardError("password is empty")
        self._copy_sensitive(password, "password")

    def copy_recovery_key(self, recovery_key: str) -> None:
        """Copy a recovery key only after an explicit user action."""

        if not isinstance(recovery_key, str) or not recovery_key.strip():
            raise ClipboardError("recovery key is empty")
        self._copy_sensitive(recovery_key.strip(), "recovery key")

    def _copy_sensitive(self, value: str, label: str) -> None:
        try:
            self.adapter.copy(value)
        except Exception as exc:  # pragma: no cover - platform-specific failure
            raise ClipboardError(f"{label} could not be copied") from exc
        self._copied_value = value
        self._copied_at = self._clock()

    def clear_expired(self) -> bool:
        """Clear an app-owned value after timeout without overwriting newer data."""

        if self._copied_value is None or self._copied_at is None:
            return False
        if self._clock() - self._copied_at < self.timeout_seconds:
            return False
        try:
            current_value = self.adapter.paste()
        except Exception as exc:  # pragma: no cover - platform-specific failure
            raise ClipboardError("clipboard could not be inspected") from exc

        copied_value = self._copied_value
        self._copied_value = None
        self._copied_at = None
        if current_value != copied_value:
            return False
        try:
            self.adapter.clear()
        except Exception as exc:  # pragma: no cover - platform-specific failure
            raise ClipboardError("clipboard could not be cleared") from exc
        return True
