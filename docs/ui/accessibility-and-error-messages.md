# Accessibility and Error-Message Behavior

**Project:** Android Password Manager
**Related checklist task:** 3.4
**Status:** Draft for review

## Accessibility requirements

### Visual presentation

- Use readable text sizes and high-contrast foreground/background combinations.
- Do not communicate success, weakness, or failure through color alone; pair color with text, icons, or symbols.
- Keep essential instructions visible without requiring a user to infer meaning from icons.
- Avoid dense paragraphs and place instructions near the related control.
- Ensure masked passwords, visible passwords, and generated passwords remain legible without exposing them unnecessarily.

### Touch and interaction

- Use comfortably sized touch targets with spacing that prevents accidental activation.
- Keep primary actions in consistent locations.
- Require confirmation for deletion and other irreversible operations.
- Do not make security actions depend on a gesture that is difficult to discover.
- Ensure the interface remains usable on supported phone screen sizes and orientations selected for testing.

### Labels and assistive technology

- Every input field has a visible label and a descriptive accessibility label where supported by Kivy and Android.
- Icon-only controls such as show/hide, copy, lock, and search have text alternatives or accessible descriptions.
- Focus order follows the visual order of the form.
- Error messages are associated with the field or action that caused them.
- The implementation must document any Kivy or Android accessibility limitation discovered during testing.

### Time and motion

- No essential security message depends on animation or a short display duration.
- Clipboard timeout is a security behavior, not a confirmation message that disappears before it can be read.
- Avoid flashing or rapidly changing visual states.

## Error-message principles

1. State what happened in plain language.
2. Tell the user what to do next when a corrective action is possible.
3. Do not expose passwords, recovery keys, key material, SQL, stack traces, file paths, or cryptographic internals.
4. Use generic authentication failures so an attacker cannot learn which secret component was valid.
5. Keep the user-facing message separate from detailed diagnostic logging.
6. Do not log the sensitive values involved in the failed operation.

## Error catalog

| Error ID | Trigger | User-facing message | Safe next action |
|---|---|---|---|
| ERR-SETUP-01 | Master-password fields differ | “The passwords do not match. Enter the same password in both fields.” | Correct the fields. |
| ERR-SETUP-02 | Password policy fails | “Use at least 8 characters with uppercase, lowercase, a number, and a special character.” | Update the password. |
| ERR-SETUP-03 | Recovery-key confirmation missing | “Confirm that you saved the recovery key before continuing.” | Review and confirm. |
| ERR-AUTH-01 | Master-password verification fails | “That password did not unlock the vault. Try again.” | Retry or choose recovery. |
| ERR-AUTH-02 | Vault metadata is invalid | “The vault could not be opened. Check the vault data or restore from an approved backup.” | Stop; do not retry destructive actions. |
| ERR-REC-01 | Recovery-key verification fails | “That recovery key was not accepted. Check the key and try again.” | Re-enter the key. |
| ERR-ENTRY-01 | App/website name missing | “Enter an app or website name.” | Complete the field. |
| ERR-ENTRY-02 | Username missing | “Enter a username.” | Complete the field. |
| ERR-ENTRY-03 | Password missing | “Enter a password or generate one.” | Complete the field. |
| ERR-ENTRY-04 | Entry save fails | “The password could not be saved. Your existing vault data was not changed.” | Retry after reviewing the form. |
| ERR-ENTRY-05 | Entry delete fails | “The password could not be deleted. Your vault was not changed.” | Retry or leave the entry intact. |
| ERR-CLIP-01 | Clipboard clear unavailable | “The password was copied, but this device may not allow automatic clipboard clearing.” | Manually clear the clipboard. |
| ERR-SESSION-01 | Session expired | “Your vault is locked to protect your passwords. Enter your master password to continue.” | Re-authenticate. |
| ERR-DATA-01 | Unsupported format/version | “This vault format is not supported by this app version.” | Stop and seek the documented recovery path. |
| ERR-SYSTEM-01 | Unexpected non-sensitive failure | “Something went wrong. No changes were saved.” | Retry safely or review diagnostics without exposing secrets. |

## Diagnostic policy

Internal diagnostics may record a stable error ID, operation category, app version, and non-sensitive state. Diagnostics must not contain:

- Master passwords
- Recovery keys
- Usernames or credential passwords
- Decrypted vault payloads
- Derived keys or nonces tied to secrets
- Full SQL statements containing sensitive values

## Acceptance checks

- Every interactive control has a label or accessible description.
- Every validation error identifies a corrective action.
- Authentication failures are generic.
- Sensitive values never appear in user-facing error text or logs.
- Color is never the only error or strength indicator.
- Accessibility limitations are documented in test results and known limitations.

