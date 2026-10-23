"""Password Manager Kivy UI shell.

This entry point is intentionally presentation-only. Later tasks will connect
the screens to application services, security, storage, and platform adapters.
"""

from kivy.app import App

from app.ui.screens import build_screen_manager


class PasswordManagerApp(App):
    """Root Kivy application for the phase-three UI shell."""

    title = "Lockbox"

    def build(self):
        return build_screen_manager()


if __name__ == "__main__":
    PasswordManagerApp().run()

