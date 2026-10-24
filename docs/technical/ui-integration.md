# UI Integration

**Related checklist task:** 6.12  
**Status:** Service-connected MVP implemented; see [final test results](../testing/final-test-results.md) for recorded device outcomes and gaps.

`VaultUiController` is the presentation boundary between Kivy screens and the
security, storage, credential, generator, strength, clipboard, and auto-lock
services. It owns the active local database connection and authenticated
session, and it rejects sensitive actions after the session locks.

The Kivy screen flow now includes vault setup, master-password login, recovery
reset, credential creation, viewing with password masking, explicit reveal and
copy, editing, confirmed deletion, app-name search, generator feedback, and
manual locking. The application entry point creates the controller using the
platform user-data directory, schedules one-second clipboard/auto-lock checks,
and closes the database on shutdown.

Android secure-window protection is enabled at startup by the platform
adapter. Desktop runs remain possible for development because the Android
`pyjnius` call is isolated behind the adapter.

Forms now scroll and controls wrap/grow with text. Android uses keyboard pan
mode. Setup requires explicit recovery-key save confirmation; navigation and
controller lock clear sensitive screen values, with a draft-preserving exception
for the entry/generator round trip. Lock cleanup includes inactive screens.

Controller tests inject a fake clipboard, and widget regressions exercise setup
confirmation, cleanup, generator navigation and scrolling. See the
[current technical guide](TECHNICAL_DOCUMENTATION.md) for platform limits.
