# Screenshot and Screen-Recording Protection

**Related checklist task:** 6.11  
**Status:** Implemented and enabled at Android application startup; physical-device verification remains part of deployment/testing.

The Android platform adapter enables `android.view.WindowManager.LayoutParams.FLAG_SECURE`
on the Kivy application window. Android uses this flag to prevent ordinary
screenshots and screen-recording capture of the application window. The flag is
applied app-wide before sensitive screens are used and is not removed during
the phase-one session. The flag mutation is dispatched through
python-for-android's `android.runnable.Runnable` because Kivy startup runs on
the SDL thread while Android window mutations must run on the activity UI
thread.

The `pyjnius` import is isolated inside the Android adapter so desktop test
runs remain possible. On Android, adapter failure raises `SecureWindowError`
and prevents the application from claiming that sensitive content is
protected. Tests inject fake activities and adapters to verify flag
application and fail-closed controller state.

This control does not protect against external cameras, a compromised Android
operating system, rooted-device capture, or content intentionally copied to
the system clipboard. Those residual limitations must remain in the user
manual and final known-limitations documentation.
