"""Session inactivity and automatic-lock controls."""

import time
from typing import Callable

from app.config import DEFAULT_SETTINGS
from app.security.vault_service import UnlockedVaultSession


class SessionControlError(ValueError):
    """Raised when an inactivity controller is configured incorrectly."""


class AutoLockController:
    """Lock an unlocked session after qualifying activity has stopped."""

    def __init__(
        self,
        session: UnlockedVaultSession,
        *,
        timeout_seconds: int = DEFAULT_SETTINGS.auto_lock_seconds,
        clock: Callable[[], float] = time.monotonic,
    ):
        if not isinstance(session, UnlockedVaultSession):
            raise SessionControlError("an unlocked vault session is required")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise SessionControlError("timeout_seconds must be a positive integer")
        if not callable(clock):
            raise SessionControlError("clock must be callable")
        self.session = session
        self.timeout_seconds = timeout_seconds
        self._clock = clock
        self._last_activity = clock() if session.is_unlocked else None

    def record_activity(self) -> bool:
        """Record qualifying foreground activity without unlocking a session."""

        if not self.session.is_unlocked:
            return False
        self._last_activity = self._clock()
        return True

    def check_auto_lock(self) -> bool:
        """Lock when the elapsed monotonic inactivity reaches the limit."""

        if not self.session.is_unlocked or self._last_activity is None:
            return False
        if self._clock() - self._last_activity < self.timeout_seconds:
            return False
        self.lock_now()
        return True

    def lock_now(self) -> None:
        """Perform an immediate manual or automatic lock transition."""

        self.session.lock()
        self._last_activity = None
