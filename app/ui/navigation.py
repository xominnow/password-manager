"""Application routes and Kivy shell construction."""

from kivy.uix.screenmanager import FadeTransition, ScreenManager


class Routes:
    """Named routes used by the presentation shell."""

    SETUP = "setup"
    LOGIN = "login"
    RECOVERY = "recovery"
    NEW_MASTER = "new_master"
    VAULT = "vault"
    ENTRY = "entry"
    DETAIL = "detail"
    GENERATOR = "generator"


def build_app_shell(controller=None, initial_route=None):
    """Build the presentation shell and register every MVP route."""

    from app.ui.screens import (
        DetailScreen,
        EntryScreen,
        GeneratorScreen,
        LoginScreen,
        SetupScreen,
        NewMasterScreen,
        RecoveryScreen,
        VaultListScreen,
    )

    manager = ScreenManager(transition=FadeTransition(duration=0.15))
    for screen_type in (
        SetupScreen,
        LoginScreen,
        RecoveryScreen,
        NewMasterScreen,
        VaultListScreen,
        EntryScreen,
        DetailScreen,
        GeneratorScreen,
    ):
        manager.add_widget(screen_type(controller=controller))

    if initial_route is None:
        initial_route = Routes.LOGIN if controller is None or controller.has_vault else Routes.SETUP
    if not manager.has_screen(initial_route):
        raise ValueError(f"Unknown initial route: {initial_route}")
    manager.current = initial_route
    if controller is not None:
        controller.on_lock = lambda: clear_sensitive_screens(manager)
    return manager


def clear_sensitive_screens(manager):
    """Clear even inactive screens when the controller locks its session."""
    for screen in manager.screens:
        screen.clear_sensitive()
