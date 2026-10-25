"""Functional Kivy screens connected to the local vault services."""

from functools import partial

from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.navigation import Routes


NAVY = (0.09, 0.20, 0.30, 1)
BLUE = (0.18, 0.50, 0.93, 1)
LIGHT_BLUE = (0.91, 0.95, 1.0, 1)
MUTED = (0.41, 0.46, 0.53, 1)
GREEN = (0.12, 0.62, 0.40, 1)
RED = (0.75, 0.18, 0.18, 1)
BODY_FONT_SIZE = sp(21.6)
LIST_ITEM_FONT_SIZE = sp(21.6)
TITLE_FONT_SIZE = sp(27)
CAPTION_FONT_SIZE = sp(16.2)


def styled_label(text, *, font_size=BODY_FONT_SIZE, color=NAVY, bold=False, height=None):
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
    label.bind(width=lambda widget, width: setattr(widget, "text_size", (width, None)))
    label.bind(texture_size=lambda widget, size: setattr(widget, "height", max(dp(height or 34), size[1] + dp(8))))
    return label


def fit_button(button, minimum_height):
    """Wrap long button labels and grow their touch targets with text."""
    button.halign = "center"
    button.valign = "middle"
    button.bind(width=lambda widget, width: setattr(widget, "text_size", (max(dp(1), width - dp(20)), None)))
    button.bind(texture_size=lambda widget, size: setattr(widget, "height", max(dp(minimum_height), size[1] + dp(20))))
    return button


def primary_button(text, callback=None, *, height=48, font_size=BODY_FONT_SIZE):
    button = Button(
        text=text,
        color=(1, 1, 1, 1),
        font_size=font_size,
        background_normal="",
        background_color=BLUE,
        size_hint_y=None,
        height=dp(height),
    )
    if callback:
        button.bind(on_release=callback)
    return fit_button(button, height)


def secondary_button(text, callback=None, *, height=44, font_size=BODY_FONT_SIZE):
    button = Button(
        text=text,
        color=NAVY,
        font_size=font_size,
        background_normal="",
        background_color=LIGHT_BLUE,
        size_hint_y=None,
        height=dp(height),
    )
    if callback:
        button.bind(on_release=callback)
    return fit_button(button, height)


def password_input(hint_text):
    return TextInput(
        hint_text=hint_text,
        font_size=BODY_FONT_SIZE,
        password=True,
        multiline=False,
        size_hint_y=None,
        height=dp(44),
    )


class BaseScreen(Screen):
    """Shared layout and controller helpers."""

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.root_layout = None
        self.status_label = None
        self.scroll = None
        self._inputs = []
        self._password_toggles = {}

    def content(self, title, subtitle=None):
        root = GridLayout(
            cols=1,
            size_hint_y=None,
            padding=(dp(24), dp(20), dp(24), dp(20)),
            spacing=dp(10),
        )
        root.bind(minimum_height=root.setter("height"))
        root.add_widget(styled_label(title, font_size=TITLE_FONT_SIZE, bold=True, height=42))
        if subtitle:
            root.add_widget(styled_label(subtitle, font_size=CAPTION_FONT_SIZE, color=MUTED, height=38))
        self.root_layout = root
        self.scroll = ScrollView(do_scroll_x=False)
        self.scroll.add_widget(root)
        self.add_widget(self.scroll)
        return root

    def status(self, text="", *, error=False):
        if self.status_label is not None:
            self.status_label.text = text
            self.status_label.color = RED if error else MUTED

    def go_to(self, screen_name, *_args):
        if self.controller is not None and self.controller.auto_lock is not None:
            self.controller.auto_lock.record_activity()
        if self.manager and self.manager.has_screen(screen_name):
            self.manager.current = screen_name

    def track_activity(self, _widget, _value):
        if self.controller is not None and self.controller.auto_lock is not None:
            self.controller.auto_lock.record_activity()

    def track_input(self, widget):
        self._inputs.append(widget)
        widget.bind(text=self.track_activity)
        widget.bind(font_size=lambda field, size: setattr(field, "height", max(dp(44), size * 1.6 + dp(20))))
        widget.height = max(widget.height, widget.font_size * 1.6 + dp(20))
        widget.bind(focus=lambda field, focused: Clock.schedule_once(lambda _: self.scroll.scroll_to(field, padding=dp(16)), 0.3) if focused and self.scroll else None)
        if self.scroll:
            self.scroll.bind(height=lambda *_: Clock.schedule_once(lambda _: self.scroll.scroll_to(widget, padding=dp(16)) if widget.focus else None, 0.1))
        return widget

    def add_password_input(self, root, hint_text, *, label="password"):
        """Add a masked field with its own explicit, consistently styled toggle."""
        field = self.track_input(password_input(hint_text))
        button = secondary_button(
            f"Show {label}", partial(self.toggle_password_visibility, field)
        )

        def update_caption(_field, masked):
            button.text = f"{'Show' if masked else 'Hide'} {label}"

        field.bind(password=update_caption)
        self._password_toggles[field] = button
        root.add_widget(field)
        root.add_widget(button)
        return field

    def toggle_password_visibility(self, field, *_args):
        """Change display masking only; do not copy, store or alter the value."""
        self.track_activity(None, None)
        field.password = not field.password

    def reset_password_visibility(self):
        for field in self._password_toggles:
            field.password = True

    def clear_sensitive(self):
        """Drop screen-held values; this does not promise memory zeroization."""
        self.reset_password_visibility()
        for widget in self._inputs:
            widget.focus = False
            widget.text = ""
        self.status("")

    def on_pre_leave(self, *_args):
        self.reset_password_visibility()
        # Preserve an unsaved credential only during its generator round trip.
        if self.name == Routes.ENTRY and self.manager.current == Routes.GENERATOR:
            for widget in self._inputs:
                widget.focus = False
            return
        self.clear_sensitive()

    def add_status(self, root):
        self.status_label = styled_label("", font_size=CAPTION_FONT_SIZE, color=MUTED, height=42)
        root.add_widget(self.status_label)


class SetupScreen(BaseScreen):
    name = Routes.SETUP

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recovery_key = ""
        self.recovery_saved = False
        root = self.content("Create your vault", "Your vault stays encrypted on this device.")
        root.add_widget(styled_label("Master password", bold=True))
        self.master = self.add_password_input(root, "At least 8 characters", label="master password")
        root.add_widget(styled_label("Confirm master password", bold=True))
        self.confirm = self.add_password_input(root, "Re-enter your master password", label="confirmation")
        self.recovery_label = styled_label("", color=GREEN, height=70)
        root.add_widget(self.recovery_label)
        self.copy_recovery_button = secondary_button("Copy recovery key", self.copy_recovery_key)
        self.copy_recovery_button.disabled = True
        root.add_widget(self.copy_recovery_button)
        self.create_button = primary_button("Create vault", self.create_vault)
        root.add_widget(self.create_button)
        self.saved_button = secondary_button("I saved my recovery key", self.confirm_saved)
        self.saved_button.disabled = True
        root.add_widget(self.saved_button)
        root.add_widget(secondary_button("Back to login", partial(self.go_to, Routes.LOGIN)))
        self.add_status(root)

    def create_vault(self, *_args):
        if self.master.text != self.confirm.text:
            self.status("Master passwords do not match.", error=True)
            return
        try:
            recovery_key = self.controller.setup(self.master.text)
        except Exception:
            self.status("Vault setup failed. Check the password requirements.", error=True)
            return
        self.recovery_key = recovery_key
        self.reset_password_visibility()
        self.master.text = ""
        self.confirm.text = ""
        self.recovery_label.text = f"Save this recovery key now:\n{recovery_key}"
        self.copy_recovery_button.disabled = False
        self.create_button.disabled = True
        self.saved_button.disabled = False
        self.status("Vault created. Save the recovery key, then sign in.")

    def copy_recovery_key(self, *_args):
        try:
            self.controller.copy_recovery_key(self.recovery_key)
            self.status("Recovery key copied. It will clear after 30 seconds.")
        except Exception:
            self.status("Recovery key could not be copied.", error=True)

    def confirm_saved(self, *_args):
        if not self.recovery_key:
            return
        self.recovery_saved = True
        self.go_to(Routes.LOGIN)

    def go_to(self, screen_name, *_args):
        if self.recovery_key and not self.recovery_saved:
            self.status("Save your recovery key, then select 'I saved my recovery key'.", error=True)
            return
        super().go_to(screen_name, *_args)

    def clear_sensitive(self):
        super().clear_sensitive()
        self.recovery_key = ""
        self.recovery_label.text = ""
        self.recovery_saved = False
        self.copy_recovery_button.disabled = True
        self.saved_button.disabled = True

    def on_pre_enter(self, *_args):
        self.create_button.disabled = bool(self.controller and self.controller.has_vault)


class LoginScreen(BaseScreen):
    name = Routes.LOGIN

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Welcome back", "Unlock your local vault")
        root.add_widget(styled_label("Master password", bold=True))
        self.master = self.add_password_input(root, "Enter your master password", label="master password")
        root.add_widget(primary_button("Unlock vault", self.login))
        root.add_widget(secondary_button("Forgot master password?", partial(self.go_to, Routes.RECOVERY)))
        root.add_widget(secondary_button("Create a new vault", partial(self.go_to, Routes.SETUP)))
        root.add_widget(styled_label("Offline by design. No account or network needed.", font_size=CAPTION_FONT_SIZE, color=MUTED, height=42))
        self.add_status(root)

    def login(self, *_args):
        try:
            self.controller.login(self.master.text)
        except Exception:
            self.status("Unable to unlock vault. Check your master password.", error=True)
            return
        self.master.text = ""
        self.go_to(Routes.VAULT)


class RecoveryScreen(BaseScreen):
    name = Routes.RECOVERY

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Recover access", "Verify your recovery key and choose a new master password.")
        root.add_widget(styled_label("Recovery key", bold=True))
        self.recovery = self.track_input(TextInput(hint_text="Enter your recovery key", font_size=BODY_FONT_SIZE, multiline=True, size_hint_y=None, height=dp(74)))
        root.add_widget(self.recovery)
        root.add_widget(primary_button("Continue", self.continue_reset))
        root.add_widget(secondary_button("Back to login", partial(self.go_to, Routes.LOGIN)))
        self.add_status(root)

    def continue_reset(self, *_args):
        if not self.recovery.text.strip():
            self.status("Enter your recovery key.", error=True)
            return
        new_master = self.manager.get_screen(Routes.NEW_MASTER)
        new_master.recovery_key = self.recovery.text.strip()
        self.go_to(Routes.NEW_MASTER)


class NewMasterScreen(BaseScreen):
    name = Routes.NEW_MASTER

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recovery_key = ""
        root = self.content("Create a new master password", "Choose a password you can remember and protect.")
        root.add_widget(styled_label("New master password", bold=True))
        self.master = self.add_password_input(root, "Enter a new master password", label="new master password")
        root.add_widget(styled_label("Confirm new master password", bold=True))
        self.confirm = self.add_password_input(root, "Re-enter the new master password", label="confirmation")
        root.add_widget(primary_button("Reset password", self.reset_password))
        root.add_widget(secondary_button("Back to login", partial(self.go_to, Routes.LOGIN)))
        self.add_status(root)

    def reset_password(self, *_args):
        if self.master.text != self.confirm.text:
            self.status("Master passwords do not match.", error=True)
            return
        try:
            self.controller.reset_master_password(self.recovery_key, self.master.text)
        except Exception:
            self.status("Recovery failed. Check the recovery key and password requirements.", error=True)
            return
        self.master.text = ""
        self.confirm.text = ""
        self.go_to(Routes.VAULT)

    def clear_sensitive(self):
        super().clear_sensitive()
        self.recovery_key = ""


class VaultListScreen(BaseScreen):
    name = Routes.VAULT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("My vault", "Encrypted locally on this device")
        self.search = self.track_input(TextInput(hint_text="Search app or website", font_size=BODY_FONT_SIZE, multiline=False, size_hint_y=None, height=dp(42)))
        self.search.bind(text=self.refresh)
        root.add_widget(self.search)
        self.entries = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.entries.bind(minimum_height=self.entries.setter("height"))
        root.add_widget(self.entries)
        root.add_widget(primary_button("+ Add credential", self.add_entry))
        root.add_widget(secondary_button("Lock vault", self.lock_vault))
        self.add_status(root)

    def on_pre_enter(self, *_args):
        self.refresh()

    def refresh(self, *_args):
        self.entries.clear_widgets()
        if self.controller is None or not self.controller.is_unlocked:
            return
        try:
            views = self.controller.search(self.search.text)
        except Exception:
            self.status("Vault is locked. Sign in again.", error=True)
            return
        if not views:
            self.entries.add_widget(styled_label("No credentials found.", color=MUTED, height=48))
            return
        for view in views:
            self.entries.add_widget(
                secondary_button(
                    f"{view.app_name}\n{view.username}",
                    partial(self.open_detail, view.entry_id),
                    height=68,
                    font_size=LIST_ITEM_FONT_SIZE,
                )
            )

    def open_detail(self, entry_id, *_args):
        self.controller.current_entry_id = entry_id
        self.go_to(Routes.DETAIL)

    def add_entry(self, *_args):
        entry = self.manager.get_screen(Routes.ENTRY)
        entry.editing_id = None
        self.go_to(Routes.ENTRY)

    def lock_vault(self, *_args):
        self.controller.lock()
        self.go_to(Routes.LOGIN)

    def clear_sensitive(self):
        super().clear_sensitive()
        self.entries.clear_widgets()


class EntryScreen(BaseScreen):
    name = Routes.ENTRY

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editing_id = None
        self.resume_from_generator = False
        root = self.content("Credential", "Save an app or website login locally")
        root.add_widget(styled_label("App or website", bold=True))
        self.app_name = self.track_input(TextInput(hint_text="Example App", font_size=BODY_FONT_SIZE, multiline=False, size_hint_y=None, height=dp(44)))
        root.add_widget(self.app_name)
        root.add_widget(styled_label("Username", bold=True))
        self.username = self.track_input(TextInput(hint_text="demo-user", font_size=BODY_FONT_SIZE, multiline=False, size_hint_y=None, height=dp(44)))
        root.add_widget(self.username)
        root.add_widget(styled_label("Password", bold=True))
        self.password = self.add_password_input(root, "Enter or generate a password")
        self.password.bind(text=self.update_strength)
        self.strength = styled_label("Strength feedback will appear here.", font_size=CAPTION_FONT_SIZE, color=MUTED, height=46)
        root.add_widget(self.strength)
        root.add_widget(secondary_button("Generate strong password", self.open_generator))
        root.add_widget(primary_button("Save credential", self.save_credential))
        root.add_widget(secondary_button("Cancel", partial(self.go_to, Routes.VAULT)))
        self.add_status(root)

    def on_pre_enter(self, *_args):
        if self.resume_from_generator:
            self.resume_from_generator = False
            return
        if self.editing_id is None:
            self.app_name.text = ""
            self.username.text = ""
            self.password.text = ""
            self.status("")
            return
        try:
            view = self.controller.view(self.editing_id)
        except Exception:
            self.status("Credential is unavailable.", error=True)
            return
        if view is not None:
            self.app_name.text = view.app_name
            self.username.text = view.username
            self.password.text = view.reveal().displayed_password
            self.update_strength()

    def update_strength(self, *_args):
        if self.controller is None or not self.password.text:
            self.strength.text = "Strength feedback will appear here."
            return
        result = self.controller.password_strength(self.password.text)
        self.strength.text = f"{result.label}: " + " ".join(result.feedback)
        self.strength.color = GREEN if result.meets_policy else MUTED

    def open_generator(self, *_args):
        generator = self.manager.get_screen(Routes.GENERATOR)
        generator.return_route = Routes.ENTRY
        self.go_to(Routes.GENERATOR)

    def save_credential(self, *_args):
        try:
            if self.editing_id is None:
                self.controller.create(self.app_name.text, self.username.text, self.password.text)
            else:
                self.controller.update(self.editing_id, self.app_name.text, self.username.text, self.password.text)
        except Exception:
            self.status("Credential could not be saved. Check all fields.", error=True)
            return
        self.editing_id = None
        self.go_to(Routes.VAULT)

    def clear_sensitive(self):
        super().clear_sensitive()
        self.editing_id = None
        self.resume_from_generator = False


class DetailScreen(BaseScreen):
    name = Routes.DETAIL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = self.content("Credential", "Saved credential")
        self.app_name = styled_label("", font_size=TITLE_FONT_SIZE, bold=True, height=42)
        root.add_widget(self.app_name)
        root.add_widget(styled_label("Username", bold=True))
        self.username = styled_label("", height=44)
        root.add_widget(self.username)
        root.add_widget(styled_label("Password", bold=True))
        self.password = styled_label("••••••••", height=44)
        root.add_widget(self.password)
        self.reveal_button = secondary_button("Show password", self.toggle_password)
        root.add_widget(self.reveal_button)
        root.add_widget(secondary_button("Copy password", self.copy_password))
        root.add_widget(styled_label("Copied passwords clear after 30 seconds.", font_size=CAPTION_FONT_SIZE, color=MUTED, height=36))
        root.add_widget(primary_button("Edit", self.edit_entry))
        root.add_widget(secondary_button("Delete", self.confirm_delete))
        root.add_widget(secondary_button("Back to vault", partial(self.go_to, Routes.VAULT)))
        self.add_status(root)

    def on_pre_enter(self, *_args):
        self.load_view()

    def load_view(self):
        try:
            view = self.controller.view(self.controller.current_entry_id)
        except Exception:
            self.status("Credential is unavailable.", error=True)
            return
        if view is None:
            self.status("Credential was not found.", error=True)
            return
        self.app_name.text = view.app_name
        self.username.text = view.username
        self.password.text = view.displayed_password
        self.reveal_button.text = "Hide password" if view.password_visible else "Show password"

    def toggle_password(self, *_args):
        try:
            view = self.controller.hide_current() if self.controller.current_view.password_visible else self.controller.reveal_current()
            self.password.text = view.displayed_password
            self.reveal_button.text = "Hide password" if view.password_visible else "Show password"
        except Exception:
            self.status("Password is unavailable.", error=True)

    def copy_password(self, *_args):
        try:
            self.controller.copy_current_password()
            self.status("Password copied. It will clear after 30 seconds.")
        except Exception:
            self.status("Reveal the password before copying.", error=True)

    def edit_entry(self, *_args):
        entry = self.manager.get_screen(Routes.ENTRY)
        entry.editing_id = self.controller.current_entry_id
        self.go_to(Routes.ENTRY)

    def confirm_delete(self, *_args):
        content = GridLayout(cols=1, size_hint_y=None, padding=dp(16), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(styled_label("Delete this credential? This cannot be undone.", height=60))
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(content)
        popup = Popup(title="Confirm deletion", content=scroll, size_hint=(0.9, 0.65), auto_dismiss=False)
        content.add_widget(secondary_button("Cancel", lambda *_: popup.dismiss()))
        content.add_widget(primary_button("Delete", lambda *_: self.delete_entry(popup)))
        popup.open()

    def delete_entry(self, popup):
        popup.dismiss()
        try:
            self.controller.delete(self.controller.current_entry_id)
        except Exception:
            self.status("Credential could not be deleted.", error=True)
            return
        self.go_to(Routes.VAULT)

    def clear_sensitive(self):
        super().clear_sensitive()
        self.app_name.text = ""
        self.username.text = ""
        self.password.text = "••••••••"
        self.reveal_button.text = "Show password"


class GeneratorScreen(BaseScreen):
    name = Routes.GENERATOR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.return_route = Routes.ENTRY
        root = self.content("Password generator", "Create a strong password for the current entry")
        root.add_widget(styled_label("Generated password", bold=True))
        self.generated = styled_label("", height=64)
        root.add_widget(self.generated)
        self.feedback = styled_label("", font_size=CAPTION_FONT_SIZE, color=GREEN, height=80)
        root.add_widget(self.feedback)
        root.add_widget(secondary_button("Regenerate", self.regenerate))
        root.add_widget(primary_button("Use password", self.use_password))
        root.add_widget(secondary_button("Cancel", partial(self.go_to, Routes.ENTRY)))

    def on_pre_enter(self, *_args):
        self.regenerate()

    def go_to(self, screen_name, *_args):
        if screen_name == Routes.ENTRY:
            self.manager.get_screen(Routes.ENTRY).resume_from_generator = True
        super().go_to(screen_name, *_args)

    def regenerate(self, *_args):
        try:
            self.generated.text = self.controller.generate_password()
            result = self.controller.password_strength(self.generated.text)
            self.feedback.text = f"{result.label}: " + " ".join(result.feedback)
        except Exception:
            self.generated.text = ""
            self.feedback.text = "Password generation failed."

    def use_password(self, *_args):
        entry = self.manager.get_screen(Routes.ENTRY)
        entry.password.text = self.generated.text
        entry.update_strength()
        self.go_to(self.return_route)

    def clear_sensitive(self):
        super().clear_sensitive()
        self.generated.text = ""
        self.feedback.text = ""
