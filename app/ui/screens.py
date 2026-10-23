"""Python-only Kivy screen layouts based on the approved UI mockups.

This module intentionally contains presentation and navigation scaffolding only.
Authentication, encryption, persistence, and clipboard behavior belong to later
application, security, storage, and platform tasks.
"""

from functools import partial

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


NAVY = (0.09, 0.20, 0.30, 1)
BLUE = (0.18, 0.50, 0.93, 1)
LIGHT_BLUE = (0.91, 0.95, 1.0, 1)
MUTED = (0.41, 0.46, 0.53, 1)


def styled_label(text, *, font_size=16, color=NAVY, bold=False, height=None):
    """Create a consistently styled label with an optional fixed height."""

    label = Label(
        text=text,
        color=color,
        font_size=font_size,
        bold=bold,
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(height or 34),
    )
    label.bind(size=lambda widget, _: setattr(widget, "text_size", widget.size))
    return label


def primary_button(text, callback=None, *, height=48):
    """Create a primary action button with an optional navigation callback."""

    button = Button(
        text=text,
        color=(1, 1, 1, 1),
        background_normal="",
        background_color=BLUE,
        size_hint_y=None,
        height=dp(height),
    )
    if callback:
        button.bind(on_release=callback)
    return button


def secondary_button(text, callback=None, *, height=44):
    """Create a secondary action button."""

    button = Button(
        text=text,
        color=NAVY,
        background_normal="",
        background_color=LIGHT_BLUE,
        size_hint_y=None,
        height=dp(height),
    )
    if callback:
        button.bind(on_release=callback)
    return button


def password_input(hint_text):
    """Create a masked password field for the UI shell."""

    return TextInput(
        hint_text=hint_text,
        password=True,
        multiline=False,
        size_hint_y=None,
        height=dp(44),
    )


class BaseScreen(Screen):
    """Shared layout helpers for the prototype screens."""

    def content(self, title, subtitle=None):
        root = BoxLayout(
            orientation="vertical",
            padding=(dp(24), dp(20), dp(24), dp(20)),
            spacing=dp(14),
        )
        root.add_widget(styled_label(title, font_size=24, bold=True, height=42))
        if subtitle:
            root.add_widget(styled_label(subtitle, font_size=14, color=MUTED, height=38))
        self.add_widget(root)
        return root

    def go_to(self, screen_name, *_args):
        self.manager.current = screen_name


class LoginScreen(BaseScreen):
    name = "login"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Welcome back", "Unlock your local vault")
        root.add_widget(styled_label("Master password", bold=True))
        root.add_widget(password_input("Enter your master password"))
        root.add_widget(primary_button("Unlock vault", partial(self.go_to, "vault")))
        root.add_widget(secondary_button("Forgot master password?", partial(self.go_to, "recovery")))
        root.add_widget(styled_label("Offline by design. No account or network needed.", font_size=13, color=MUTED, height=54))


class RecoveryScreen(BaseScreen):
    name = "recovery"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Recover access", "Use the recovery key saved during setup.")
        root.add_widget(styled_label("Recovery key", bold=True))
        root.add_widget(TextInput(hint_text="Enter your recovery key", multiline=True, size_hint_y=None, height=dp(86)))
        root.add_widget(styled_label("The recovery key is never stored by the app. If both credentials are lost, the vault cannot be recovered.", font_size=13, color=MUTED, height=62))
        root.add_widget(primary_button("Verify key", partial(self.go_to, "new_master")))
        root.add_widget(secondary_button("Back to login", partial(self.go_to, "login")))


class NewMasterScreen(BaseScreen):
    name = "new_master"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Create a new master password", "Choose a password you can remember and protect.")
        root.add_widget(styled_label("New master password", bold=True))
        root.add_widget(password_input("Enter a new master password"))
        root.add_widget(styled_label("Confirm new master password", bold=True))
        root.add_widget(password_input("Re-enter the new master password"))
        root.add_widget(primary_button("Reset password", partial(self.go_to, "vault")))


class VaultListScreen(BaseScreen):
    name = "vault"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("My vault", "Encrypted locally on this device")
        search = TextInput(hint_text="Search app or website", multiline=False, size_hint_y=None, height=dp(42))
        root.add_widget(search)

        entries = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        entries.bind(minimum_height=entries.setter("height"))
        entries.add_widget(secondary_button("Example App\n demo-user", partial(self.go_to, "detail"), height=68))
        entries.add_widget(secondary_button("Bank Demo\n test-account", partial(self.go_to, "detail"), height=68))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(entries)
        root.add_widget(scroll)
        root.add_widget(primary_button("+ Add credential", partial(self.go_to, "entry")))
        root.add_widget(secondary_button("Lock vault", partial(self.go_to, "login")))


class EntryScreen(BaseScreen):
    name = "entry"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("New credential", "Save an app or website login locally")
        root.add_widget(styled_label("App or website", bold=True))
        root.add_widget(TextInput(hint_text="Example App", multiline=False, size_hint_y=None, height=dp(44)))
        root.add_widget(styled_label("Username", bold=True))
        root.add_widget(TextInput(hint_text="demo-user", multiline=False, size_hint_y=None, height=dp(44)))
        root.add_widget(styled_label("Password", bold=True))
        root.add_widget(password_input("Enter or generate a password"))
        root.add_widget(secondary_button("Generate strong password", partial(self.go_to, "generator")))
        root.add_widget(styled_label("Strength feedback will appear here.", font_size=13, color=MUTED, height=30))
        root.add_widget(primary_button("Save credential", partial(self.go_to, "vault")))


class DetailScreen(BaseScreen):
    name = "detail"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Example App", "Saved credential")
        root.add_widget(styled_label("Username", bold=True))
        root.add_widget(styled_label("demo-user", height=44))
        root.add_widget(styled_label("Password", bold=True))
        root.add_widget(styled_label("••••••••••", height=44))
        root.add_widget(secondary_button("Show password", height=44))
        root.add_widget(secondary_button("Copy password", height=44))
        root.add_widget(styled_label("Copied passwords clear after 30 seconds.", font_size=13, color=MUTED, height=36))
        root.add_widget(primary_button("Edit", partial(self.go_to, "entry")))
        root.add_widget(secondary_button("Delete", partial(self.go_to, "vault")))
        root.add_widget(secondary_button("Back to vault", partial(self.go_to, "vault")))


class GeneratorScreen(BaseScreen):
    name = "generator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Password generator", "Create a password for the current entry")
        root.add_widget(styled_label("Generated password", bold=True))
        root.add_widget(styled_label("R7!mK2@qP9#v", height=64))
        root.add_widget(styled_label("Strong", color=(0.12, 0.62, 0.40, 1), bold=True))
        root.add_widget(styled_label("✓ 8+ characters\n✓ Uppercase letter\n✓ Lowercase letter\n✓ Number\n✓ Special character", font_size=14, height=120))
        root.add_widget(secondary_button("Regenerate"))
        root.add_widget(primary_button("Use password", partial(self.go_to, "entry")))


def build_screen_manager():
    """Build the presentation-only screen manager."""

    from kivy.uix.screenmanager import ScreenManager

    manager = ScreenManager()
    for screen in (
        LoginScreen(),
        RecoveryScreen(),
        NewMasterScreen(),
        VaultListScreen(),
        EntryScreen(),
        DetailScreen(),
        GeneratorScreen(),
    ):
        manager.add_widget(screen)
    manager.current = "login"
    return manager

