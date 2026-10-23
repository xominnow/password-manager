# Functional Requirements

**Project:** Android Password Manager
**Related checklist task:** 1.1
**Status:** Draft for review

## Primary actor

The primary actor is a single local user who manages credentials on one Android device.

## User stories

| ID | User story | Acceptance summary |
|---|---|---|
| FR-01 | As a new user, I want to create a master password so that I can protect my vault. | The app accepts a valid master password, confirms it, initializes the vault, and does not store the plaintext password. |
| FR-02 | As a returning user, I want to unlock my vault with my master password. | Correct credentials unlock the vault; incorrect credentials are rejected. |
| FR-03 | As a new user, I want a recovery key so that I can regain access if I forget my master password. | The app generates a one-time recovery key, displays it once, and requires setup confirmation. |
| FR-04 | As a user, I want to reset my master password with my recovery key. | A valid recovery key permits creation of a new master password without exposing vault contents. |
| FR-05 | As a user, I want to add an app or website credential. | The app stores an app/website name, username, and password in the encrypted vault. |
| FR-06 | As a user, I want to view a saved credential while keeping the password hidden by default. | The app displays the entry and masks the password until the user explicitly reveals it. |
| FR-07 | As a user, I want to edit an existing credential. | The app allows the name, username, and password to be updated and saved. |
| FR-08 | As a user, I want to delete an existing credential. | The app requires confirmation before permanently deleting the selected entry. |
| FR-09 | As a user, I want to search by app or website name. | Matching entries are shown without requiring network access. |
| FR-10 | As a user, I want to generate a strong password. | Generated passwords are at least eight characters and include uppercase, lowercase, number, and special-character classes. |
| FR-11 | As a user, I want password-strength feedback. | The app evaluates an entered or generated password and displays understandable strength feedback. |
| FR-12 | As a user, I want to copy a password to the clipboard. | The selected password is copied only after an explicit user action. |
| FR-13 | As a user, I want copied passwords removed from the clipboard automatically. | The copied password is cleared after 30 seconds or sooner when the app can safely do so. |
| FR-14 | As a user, I want the vault to lock after inactivity. | The app locks after two minutes without user activity and requires the master password to unlock. |
| FR-15 | As a user, I want screenshots and screen recording blocked on sensitive screens. | Android secure-window behavior is enabled while sensitive vault content is displayed. |
| FR-16 | As a user, I want the app to work offline. | Core functions work without Internet access and the app requests no Internet permission. |
| FR-17 | As a user, I want to lock the vault manually. | A visible lock or logout action immediately clears the active session and returns to login. |
| FR-18 | As a user, I want clear validation messages. | Invalid or incomplete input is identified without exposing passwords or cryptographic details. |

## Use cases

### UC-01 — Initialize the vault

**Actor:** New user

**Preconditions:** No vault has been initialized on the device.

**Main flow:**

1. The user opens the app.
2. The app requests a master password and confirmation.
3. The user submits matching passwords that meet the configured policy.
4. The app generates a random vault-encryption key.
5. The app generates and displays a one-time recovery key.
6. The user confirms that the recovery key has been saved.
7. The app stores only the protected key material and initializes the encrypted vault.
8. The app opens the authenticated vault session.

**Alternate flows:**

- If the passwords do not match or fail validation, the app explains the problem and does not initialize the vault.
- If the user does not confirm recovery-key storage, setup remains incomplete.

### UC-02 — Unlock the vault

**Actor:** Returning user

**Preconditions:** A vault exists and the app is locked.

**Main flow:**

1. The user enters the master password.
2. The app derives the authentication key.
3. The app verifies and unwraps the vault-encryption key.
4. The app opens the vault.

**Alternate flow:**

- An incorrect password leaves the vault locked and displays a generic failure message.

### UC-03 — Recover access and reset the master password

**Actor:** User who forgot the master password

**Preconditions:** A recovery key exists and the vault is locked.

**Main flow:**

1. The user selects recovery.
2. The user enters the recovery key.
3. The app verifies and unwraps the vault-encryption key through the recovery path.
4. The user creates and confirms a new master password.
5. The app re-wraps the vault-encryption key with the new master-password key.
6. The app invalidates the previous master-password wrapping material.
7. The app opens the vault.

**Alternate flows:**

- An invalid recovery key leaves the vault locked.
- A recovery-key reset does not reveal the recovery key or existing plaintext credentials.

### UC-04 — Manage a credential

**Actor:** Authenticated user

**Preconditions:** The vault is unlocked.

**Main flow:**

1. The user selects add, edit, view, or delete.
2. The app displays the relevant form or confirmation dialog.
3. The user submits the requested action.
4. The app validates the input.
5. The app encrypts or removes the affected data.
6. The app refreshes the vault list.

**Alternate flows:**

- Invalid input is rejected with a clear message.
- Deletion is cancelled unless explicitly confirmed.
- A locked session redirects the user to login.

### UC-05 — Generate, evaluate, and copy a password

**Actor:** Authenticated user

**Preconditions:** The vault is unlocked and an entry form is open.

**Main flow:**

1. The user requests a generated password.
2. The app creates a password meeting the configured character requirements.
3. The app displays strength feedback.
4. The user optionally copies the password.
5. The app clears the clipboard after 30 seconds.

### UC-06 — Automatic and manual locking

**Actor:** Authenticated user or inactivity timer

**Main flow:**

1. The user selects lock, or two minutes pass without activity.
2. The app closes the active vault session.
3. The app returns to the login screen.
4. The user must authenticate again to access vault contents.

## Explicitly deferred functionality

- Biometric unlock
- Cloud synchronization
- Multi-user support
- Browser extensions
- Cross-platform clients

