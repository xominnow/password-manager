# Clipboard Copying

**Related checklist task:** 6.8  
**Status:** Implemented as a platform adapter and service with app-owned 30-second timeout clearing.

`ClipboardService.copy_password()` requires an unlocked vault session and a
`CredentialView` that the caller has explicitly revealed. It copies only the
password, never the app name or username, and rejects masked views. The
service does not log or persist clipboard contents.

After a successful copy, the service records only the copied value and a
monotonic timestamp in memory. At 30 seconds, `clear_expired()` reads the
current clipboard and clears it only when it exactly matches the value copied
by this app. A newer value is never overwritten, and the tracking state is
discarded after the comparison.

The platform boundary is represented by `ClipboardAdapter`. The Android
implementation delegates to Kivy's clipboard API, while tests inject a fake
adapter. The adapter also exposes read and clear operations needed by the
30-second timeout task. Clipboard failures are translated to a generic
`ClipboardError`.

The clipboard remains a platform-owned surface and may be visible to other
apps. The comparison cannot identify whether another app independently copied
the same text, which is a documented platform limitation.

Explicit setup recovery-key copying uses the same timeout tracker. Timer checks
run through the application event loop and are not guaranteed while suspended.
Samsung keyboard history retained a test password; remediation was explicitly
skipped. Android sensitive-clip metadata is not explicitly set by the adapter.
See [current technical guide](TECHNICAL_DOCUMENTATION.md) for the final behavior.
