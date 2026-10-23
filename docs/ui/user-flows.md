# Screen Map and User Flows

**Project:** Android Password Manager
**Related checklist task:** 3.1
**Status:** Draft for review

## Screen map

| Screen ID | Screen | Purpose | Sensitive content |
|---|---|---|---|
| S-01 | Welcome / setup | Start first-time vault initialization. | No credentials yet; secure-window behavior enabled. |
| S-02 | Master-password setup | Create and confirm the master password. | Password input. |
| S-03 | Recovery-key confirmation | Display and confirm the one-time recovery key. | Recovery key. |
| S-04 | Login | Unlock an existing vault. | Master-password input. |
| S-05 | Recovery entry | Accept the recovery key for master-password reset. | Recovery-key input. |
| S-06 | New master password | Create a replacement master password after recovery. | Password input. |
| S-07 | Vault list | Search and select saved entries. | App names and credential summaries. |
| S-08 | Add credential | Create a new app/website credential. | Username and password. |
| S-09 | Credential detail | View one saved entry with masked password. | Username and password. |
| S-10 | Edit credential | Update an existing entry. | Username and password. |
| S-11 | Password generator | Generate and accept a strong password. | Generated password. |
| S-12 | Strength feedback | Explain password-strength result. | Candidate password. |
| S-13 | Lock confirmation / locked state | End the active session. | No vault contents when locked. |
| S-14 | Error and validation states | Explain invalid or failed operations. | Must not reveal sensitive details. |

## Navigation overview

```text
No vault ──> Welcome ──> Master-password setup ──> Recovery-key confirmation ──> Vault list
                                                                                      │
Existing vault ──> Login ─────────────────────────────────────────────────────────────┘
       │                                                                              │
       └── Forgot master password ──> Recovery entry ──> New master password ─────────┘

Vault list ──> Add credential ──> Generator / strength feedback ──> Vault list
     │
     ├──> Credential detail ──> Edit credential ──> Vault list
     ├──> Credential detail ──> Copy password ──> Clipboard clears after 30 seconds
     └──> Lock ──> Login
```

## Flow UF-01 — First-time setup

1. Open the app.
2. Select setup.
3. Enter and confirm the master password.
4. Continue only if the password meets the policy.
5. Display the recovery key in a protected screen.
6. Require the user to confirm that the key has been saved.
7. Initialize the encrypted vault.
8. Transition to the vault list.

Failure states:

- Passwords do not match.
- Password policy is not satisfied.
- Recovery-key confirmation is incomplete.
- Vault initialization fails.

## Flow UF-02 — Login

1. Open the app with an existing vault.
2. Enter the master password.
3. Select unlock.
4. Derive and verify the master wrapper.
5. Transition to the vault list on success.

Failure states:

- Incorrect password.
- Malformed or tampered vault metadata.
- Unsupported vault version.

## Flow UF-03 — Recovery and master-password reset

1. Select forgot master password.
2. Enter the recovery key.
3. Verify the recovery wrapper.
4. Enter and confirm a new master password.
5. Replace the master wrapper.
6. Preserve the recovery wrapper.
7. Transition to the vault list.

Failure states:

- Invalid recovery key.
- New password does not meet policy.
- Wrapper update fails.

## Flow UF-04 — Add credential

1. Select add from the vault list.
2. Enter an app or website name.
3. Enter a username.
4. Enter a password or open the generator.
5. Review strength feedback.
6. Save the entry.
7. Encrypt and persist the entry.
8. Return to the vault list with the new entry visible.

## Flow UF-05 — View, copy, edit, and delete

1. Select an entry from the vault list.
2. Display app/website name and username.
3. Mask the password by default.
4. Permit explicit reveal, copy, edit, or delete actions.
5. Require confirmation before deletion.
6. Return to the vault list after a successful update or deletion.

## Flow UF-06 — Generate and evaluate a password

1. Open the generator from an entry form.
2. Generate a password meeting all required character classes.
3. Display strength feedback.
4. Permit regeneration or acceptance.
5. Return the accepted value to the entry form without copying it automatically.

## Flow UF-07 — Locking and inactivity

1. The user may select lock at any time.
2. The app tracks qualifying activity while unlocked.
3. After two minutes without activity, the app transitions to locked.
4. The app clears or invalidates active session references.
5. The user must log in again before viewing credentials.

## Flow UF-08 — Clipboard timeout

1. The user explicitly selects copy password.
2. The app writes the password to the clipboard.
3. The app starts a 30-second timeout.
4. If the clipboard still contains the app's copied value, the app clears it.
5. If another value replaced it, the app does not overwrite the newer value.

## UI behavior rules

- Sensitive screens use secure-window behavior.
- Passwords are masked by default.
- Destructive actions require confirmation.
- Errors identify corrective action without revealing cryptographic details.
- Navigation must never bypass the locked-session check.
- Biometric unlock is not shown in phase-one screens.

