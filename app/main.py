"""Password Manager Kivy application entry point."""

from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

from app.config import DEFAULT_SETTINGS
from app.platform.secure_window import AndroidSecureWindowAdapter
from app.ui.controller import VaultUiController
from app.ui.navigation import build_app_shell


class PasswordManagerApp(App):
    """Root Kivy application for the phase-three UI shell."""

    title = DEFAULT_SETTINGS.app_name

    def build(self):
        # SDL2 Android does not support Kivy's resize mode. Pan keeps the
        # bottom of the form above the keyboard while forms remain scrollable.
        Window.softinput_mode = "pan"
        database_path = Path(self.user_data_dir) / "vault.sqlite3"
        self.controller = VaultUiController(database_path)
        self.screen_manager = build_app_shell(self.controller)
        self._timer = Clock.schedule_interval(self._tick, 1.0)
        return self.screen_manager

    def _tick(self, _elapsed):
        self.controller.clear_expired_clipboard()
        if self.controller.check_auto_lock() and self.screen_manager.has_screen("login"):
            self.screen_manager.current = "login"

    def on_start(self):
        """Enable Android secure-window protection before sensitive UI use."""

        if platform == "android":
            AndroidSecureWindowAdapter().enable()

    def on_stop(self):
        if hasattr(self, "_timer"):
            self._timer.cancel()
        if hasattr(self, "controller"):
            self.controller.close()


if __name__ == "__main__":
    PasswordManagerApp().run()

