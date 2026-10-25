"""Application-facing coordinator for the functional Kivy screens."""

from pathlib import Path

from app.platform.clipboard import ClipboardAdapter, ClipboardService, KivyClipboardAdapter
from app.security.password_generator import generate_password
from app.security.vault_service import LocalVaultService, UnlockedVaultSession
from app.services.credentials import CredentialService, CredentialView
from app.services.password_strength import PasswordStrength, evaluate_password
from app.services.session import AutoLockController
from app.storage.sqlite import VaultDatabase


class UiControllerError(ValueError):
    """Raised when a UI action cannot be completed safely."""


class VaultUiController:
    """Coordinate authenticated application actions for the Kivy presentation layer."""

    def __init__(self, database_path: str | Path, clipboard_adapter: ClipboardAdapter | None = None):
        self.database = VaultDatabase(database_path)
        self.vault_service = LocalVaultService(self.database)
        self.credentials = CredentialService(self.database)
        self.clipboard = ClipboardService(clipboard_adapter or KivyClipboardAdapter())
        self.session: UnlockedVaultSession | None = None
        self.auto_lock: AutoLockController | None = None
        self.current_entry_id: str | None = None
        self.current_view: CredentialView | None = None
        self.on_lock = None

    @property
    def has_vault(self) -> bool:
        return self.database.get_vault_id() is not None

    @property
    def is_unlocked(self) -> bool:
        return self.session is not None and self.session.is_unlocked

    def _active_session(self) -> UnlockedVaultSession:
        if self.session is None or not self.session.is_unlocked:
            raise UiControllerError("vault is locked")
        if self.auto_lock is not None:
            self.auto_lock.record_activity()
        return self.session

    def setup(self, master_password: str):
        result = self.vault_service.setup(master_password)
        return result.recovery_key

    def login(self, master_password: str) -> None:
        self.session = self.vault_service.login(master_password)
        self.auto_lock = AutoLockController(self.session)

    def reset_master_password(self, recovery_key: str, new_master_password: str) -> None:
        self.session = self.vault_service.reset_master_password(recovery_key, new_master_password)
        self.auto_lock = AutoLockController(self.session)

    def lock(self) -> None:
        if self.auto_lock is not None:
            self.auto_lock.lock_now()
        elif self.session is not None:
            self.session.lock()
        self.current_entry_id = None
        self.current_view = None
        if self.on_lock is not None:
            self.on_lock()

    def check_auto_lock(self) -> bool:
        if self.auto_lock is None:
            return False
        locked = self.auto_lock.check_auto_lock()
        if locked:
            self.current_entry_id = None
            self.current_view = None
            if self.on_lock is not None:
                self.on_lock()
        return locked

    def search(self, query: str = "") -> tuple[CredentialView, ...]:
        return self.credentials.search(self._active_session(), query)

    def create(self, app_name: str, username: str, password: str):
        return self.credentials.create(self._active_session(), app_name, username, password)

    def view(self, entry_id: str) -> CredentialView | None:
        session = self._active_session()
        self.current_entry_id = entry_id
        self.current_view = self.credentials.view(session, entry_id)
        return self.current_view

    def update(self, entry_id: str, app_name: str, username: str, password: str):
        result = self.credentials.update(self._active_session(), entry_id, app_name, username, password)
        self.current_entry_id = entry_id
        self.current_view = self.credentials.view(self.session, entry_id)
        return result

    def delete(self, entry_id: str) -> bool:
        deleted = self.credentials.delete(self._active_session(), entry_id, confirmed=True)
        if deleted and self.current_entry_id == entry_id:
            self.current_entry_id = None
            self.current_view = None
        return deleted

    def reveal_current(self) -> CredentialView:
        if self.current_view is None:
            raise UiControllerError("credential is not selected")
        self.current_view = self.current_view.reveal()
        return self.current_view

    def hide_current(self) -> CredentialView:
        if self.current_view is None:
            raise UiControllerError("credential is not selected")
        self.current_view = self.current_view.hide()
        return self.current_view

    def copy_current_password(self) -> None:
        if self.current_view is None or self.session is None:
            raise UiControllerError("credential is not selected")
        self.clipboard.copy_password(self.session, self.current_view)

    def copy_recovery_key(self, recovery_key: str) -> None:
        self.clipboard.copy_recovery_key(recovery_key)

    def clear_expired_clipboard(self) -> bool:
        return self.clipboard.clear_expired()

    @staticmethod
    def generate_password(length: int = 20) -> str:
        return generate_password(length)

    @staticmethod
    def password_strength(password: str) -> PasswordStrength:
        return evaluate_password(password)

    def close(self) -> None:
        self.lock()
        self.database.close()
