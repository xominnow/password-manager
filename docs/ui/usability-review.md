# Usability Review

**Project:** Android Password Manager
**Related checklist task:** 3.3
**Review type:** Heuristic review of approved flows and mockups
**Status:** Draft for review

## Target-user considerations

The target user may reuse passwords, feel uncomfortable with security terminology, and have limited experience with password-management applications. The interface must therefore reduce decision-making, explain consequences in plain language, and make recovery behavior visible before setup is completed.

This is a design review, not a substitute for testing with representative users.

## Usability requirements

1. Use plain-language labels such as “Master password,” “Recovery key,” “Copy password,” and “Lock vault.”
2. Avoid exposing implementation terms such as KDF, key-encryption key, nonce, ciphertext, or authentication tag.
3. Keep one primary action per screen.
4. Use consistent placement for Back, Continue, Save, Cancel, and Lock actions.
5. Mask passwords by default and provide an obvious show/hide control.
6. Explain the recovery key before the user leaves setup.
7. Make destructive actions explicit and require confirmation.
8. Show corrective validation messages beside the affected field.
9. Use sufficiently large touch targets and readable text on supported phone sizes.
10. Do not rely on color alone to communicate password strength or errors.
11. Keep the search and add-entry actions visible from the vault list.
12. Use synthetic examples in mockups and help text; never encourage entry of real secrets during testing.

## Flow-by-flow findings

### Setup

**Risk:** Users may skip or misunderstand the recovery-key requirement.

**Recommendation:** Explain in one short sentence that the key is the only planned way to reset a forgotten master password. Require a deliberate confirmation before continuing.

### Login

**Risk:** “Unlock vault” may be unfamiliar to some users.

**Recommendation:** Keep “Unlock vault” but add the supporting phrase “Open your saved passwords.” Do not display technical failure details.

### Recovery

**Risk:** Users may expect the app to email or text a replacement key.

**Recommendation:** State clearly that recovery is offline and that the app cannot retrieve a lost recovery key.

### Vault list

**Risk:** Users may not know whether an item is an app or website.

**Recommendation:** Label the field “App or website” consistently and show the username as secondary information.

### Add and edit

**Risk:** Users may create weak passwords or save incomplete entries.

**Recommendation:** Provide the generator beside the password field, show strength feedback immediately, and explain missing required fields in plain language.

### Credential detail

**Risk:** Users may accidentally expose a password while trying to copy it.

**Recommendation:** Keep the password masked by default, separate “Show” and “Copy password,” and show a brief confirmation that the clipboard will clear automatically.

### Delete

**Risk:** A user may delete an entry accidentally.

**Recommendation:** Use a confirmation dialog naming the app/website, with “Cancel” as the safe default.

### Auto-lock

**Risk:** A user may think the app lost data after it locks.

**Recommendation:** Explain that locking protects the vault and that saved entries remain available after re-authentication.

## Accessibility and readability checks

- Use high-contrast text and controls.
- Use labels in addition to icons.
- Avoid small secondary text for essential instructions.
- Keep error messages short and actionable.
- Support keyboard focus order where Android input methods expose it.
- Ensure fields have descriptive labels for screen-reader compatibility where supported by the Kivy implementation.
- Do not use flashing, animated, or time-critical UI for security messages.

## Recommended wording

| Situation | Recommended wording |
|---|---|
| Wrong master password | “That password did not unlock the vault. Try again.” |
| Wrong recovery key | “That recovery key was not accepted. Check the key and try again.” |
| Weak password | “Use at least 8 characters with uppercase, lowercase, a number, and a special character.” |
| Recovery warning | “If you forget your master password, this recovery key is the only way to reset it.” |
| Auto-lock | “Your vault is locked to protect your passwords. Enter your master password to continue.” |
| Delete confirmation | “Delete the saved password for [app or website]? This cannot be undone.” |
| Clipboard notice | “Copied. The clipboard will be cleared after 30 seconds.” |

## Review outcome

The mockups support the target user when the implementation preserves the following priorities:

1. One clear primary action per screen.
2. Plain language instead of cryptographic terminology.
3. Visible recovery consequences.
4. Safe defaults for password visibility and deletion.
5. Clear, actionable validation feedback.

