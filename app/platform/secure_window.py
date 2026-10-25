"""Android secure-window controls for screenshot and recording protection."""

from threading import Event
from typing import Protocol


class SecureWindowError(RuntimeError):
    """Raised when Android secure-window protection cannot be enabled."""


class SecureWindowAdapter(Protocol):
    """Platform contract for enabling an app-wide secure window."""

    def enable(self) -> None:
        """Enable screenshot and screen-recording protection."""


def apply_secure_flag(activity, flag: int) -> None:
    """Apply a secure-window flag to a testable Android activity object."""

    if activity is None:
        raise SecureWindowError("Android activity is unavailable")
    try:
        window = activity.getWindow()
        window.addFlags(flag)
    except Exception as exc:  # pragma: no cover - Android-specific failure
        raise SecureWindowError("secure-window protection could not be enabled") from exc


def apply_secure_flag_on_ui_thread(activity, flag: int, runnable_factory, *, timeout: float = 5.0) -> None:
    """Apply ``FLAG_SECURE`` through Android's UI thread and wait for completion.

    Kivy's startup callback runs on the SDL thread, while Android window
    mutations must run on the ``PythonActivity`` thread. ``runnable_factory``
    is injected so this boundary remains testable without an Android runtime.
    """

    completed = Event()
    failure: list[Exception] = []

    def apply_on_ui_thread() -> None:
        try:
            apply_secure_flag(activity, flag)
        except Exception as exc:  # pragma: no cover - callback executes on Android
            failure.append(exc)
        finally:
            completed.set()

    runnable_factory(apply_on_ui_thread)()
    if not completed.wait(timeout):
        raise SecureWindowError("secure-window protection UI operation timed out")
    if failure:
        raise SecureWindowError("secure-window protection could not be enabled") from failure[0]


class AndroidSecureWindowAdapter:
    """Enable Android ``FLAG_SECURE`` using the python-for-android runtime."""

    def enable(self) -> None:
        try:
            from android.runnable import Runnable
            from jnius import autoclass

            python_activity = autoclass("org.kivy.android.PythonActivity")
            layout_params = autoclass("android.view.WindowManager$LayoutParams")
            activity = python_activity.mActivity
            apply_secure_flag_on_ui_thread(
                activity,
                layout_params.FLAG_SECURE,
                Runnable,
            )
        except SecureWindowError:
            raise
        except Exception as exc:  # pragma: no cover - Android-specific failure
            raise SecureWindowError("secure-window protection is unavailable") from exc


class SecureWindowController:
    """Small application-facing wrapper that tracks successful enablement."""

    def __init__(self, adapter: SecureWindowAdapter):
        self.adapter = adapter
        self.enabled = False

    def enable(self) -> None:
        self.adapter.enable()
        self.enabled = True
