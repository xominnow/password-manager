# Two-Minute Inactivity Auto-Lock

**Related checklist task:** 6.10  
**Status:** Integrated with Kivy periodic checks and screen cleanup; explicit pause/resume hooks are not implemented.

`AutoLockController` starts a monotonic inactivity timer when constructed with
an unlocked session. Qualifying foreground events call `record_activity()`.
The controller does not unlock a session or treat background time as activity.

`check_auto_lock()` locks the session at or beyond the configured 120-second
limit. The lock clears the session's in-memory vault key through
`UnlockedVaultSession.lock()` and discards the activity timestamp. The UI and
Android lifecycle handling should check before displaying sensitive content on
resume. The current app schedules one-second foreground checks, without explicit
pause/resume hooks; a >2-minute background return passed on the test phone.
Controller locking also clears inactive screen values. See
[current technical guide](TECHNICAL_DOCUMENTATION.md).

The clock is injectable for deterministic tests. The implementation uses a
monotonic source rather than wall-clock time, and manual `lock_now()` is
immediate and cannot be reversed by activity events.
