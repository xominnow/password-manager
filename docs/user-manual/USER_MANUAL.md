# Lockbox user manual

Prepared 2026-10-24. Covers the current capstone source and its revised interface.
Lockbox is an Android password-manager prototype for one person on one device.
Use test accounts during evaluation; it has not undergone an independent
production security audit.

## Before you start

For illustrated screens, see the [UI capture gallery](../ui/screenshots/README.md).
These are synthetic desktop illustrations; phone appearance can differ.

You need an Android phone running Android 8.0 or newer with a supported ARM
processor. Testing was reported on a Samsung Galaxy S25+ with Android 17;
compatibility with every Android phone has not been verified.

Your **vault** is the collection of saved logins stored on this phone. Your
**master password** unlocks the vault. Your **recovery key** lets you replace
a forgotten master password while the vault still exists.

There is no online Lockbox account, email recovery, cloud synchronization,
backup/export feature, or automatic transfer to another phone. Losing the
phone, uninstalling the app, or clearing its data can permanently remove the
vault. A recovery key cannot restore deleted vault data.

## Install Lockbox

1. Open the project's [GitHub releases page](https://github.com/xominnow/password-manager/releases).
2. Open the intended release and expand **Assets**. Download the file ending
   in `.apk`; the source-code ZIP is not the Android installer.
3. If downloading on a computer, transfer the APK to your phone.
4. Open the APK in the phone's file manager. If prompted, allow installation
   from that source and follow the phone's installation prompts.
5. Open **Lockbox**. You can revoke the file manager's installation permission
   afterward through Android settings.

Use the `v0.1.0` snapshot release for this revised interface; the older
`Lockbox_V0.1.0` asset remains unchanged. Compare the
[snapshot checksum](../release/final-source-snapshot.md), because both retain
app version 0.1.0. This manual includes revised scrolling, screen cleanup and
the **I saved my recovery key** button. The newly rebuilt snapshot still needs
a fresh physical-phone smoke test; report missing controls to the maintainer.

Python, WSL, and development tools are not required to use the installed app.
Once installed, Lockbox's vault functions work without Internet access.

## Create your vault

1. On **Create your vault**, enter a master password and enter it again in
   **Confirm master password**.
2. Use at least eight characters, including an uppercase letter, a lowercase
   letter, a number, and a punctuation symbol such as `!`, `@`, or `#`.
   The two entries must match. Choose a unique password you can remember;
   examples from project documentation are not suitable personal passwords.
3. Tap **Create vault**. Lockbox displays a recovery key.
4. Save that key privately before closing the screen. New keys have exactly
   16 letters and numbers and are case-sensitive. You may tap **Copy recovery
   key** to copy it, but a clipboard copy alone is not a durable saved record.
5. Tap **I saved my recovery key** to confirm and continue to login. The
   revised app blocks **Back to login** while the displayed key is unconfirmed.
6. Enter your master password and tap **Unlock vault**.

The recovery key is displayed during setup and cannot be retrieved later
through the app. Do not leave setup or close the app before saving it. Keep it
separate from the phone and do not send it in bug reports. Anyone with both
the key and access to the vault data may be able to reset its master password.

If a vault already exists, **Create a new vault** does not create a second
vault or overwrite the existing one. Use login or recovery instead.

## Unlock and lock

On **Welcome back**, enter the master password and tap **Unlock vault**.
An incorrect password leaves the vault locked. Check typing and capitalization
before retrying.

From **My vault**, tap **Lock vault** when finished. Lockbox also locks after
two minutes of inactivity. Enter the master password again to continue. Saved
entries remain, but unsaved edits may be discarded. Save changes before
leaving an entry or waiting for the app to lock.

## Add a saved login

1. On **My vault**, tap **+ Add credential**.
2. Fill in **App or website**, **Username**, and **Password**. All three fields
   are required. Use a recognizable name for the app or website.
3. Enter a password or use the generator described below. Strength feedback
   appears while you type.
4. Tap **Save credential**. The entry appears in your vault.

Scroll vertically if the keyboard or larger text makes controls fall outside
the visible area. You may dismiss the keyboard to reach controls as well.
**Cancel** returns without saving a new entry or the current changes.

## Generate a password

1. While adding or editing an entry, tap **Generate strong password**.
2. Review the generated password and strength feedback. The current interface
   generates 20-character passwords containing uppercase, lowercase, digits,
   and punctuation; it does not offer a length-setting control.
3. Tap **Regenerate** for another password, or **Use password** to place it
   in the entry. **Cancel** returns to the entry without applying it.
4. Tap **Save credential** to store the entry.

Lockbox does not change the password on the actual website or application.
Coordinate changes with that service so its password matches your saved
entry. Strength feedback is guidance, not a guarantee of account security.

## Find, view, and copy a login

1. On **My vault**, enter part of the app or website name in the search field.
   Search ignores capitalization. Clear the field to show all entries.
   The search uses app/website names, not usernames or passwords.
2. Tap an entry to open its details. The password starts hidden.
3. Tap **Show password** to reveal it and **Hide password** to conceal it.
4. To copy, reveal the password first, then tap **Copy password**. Switch to
   the intended login field and paste it. Only the password is copied.
5. Tap **Back to vault** when finished.

The app attempts to clear its copied value after 30 seconds while its timer
is running, and avoids replacing newer text you copied. Device clearing is
not guaranteed: Samsung Keyboard history retained a copied test password in
testing. The history fix was skipped for this project. Clipboard history may
retain passwords and recovery keys even after the active clipboard changes.
Remove those history entries manually using your keyboard's controls; do not
rely on the app's copied/cleared message as proof that all copies disappeared.

## Edit or delete an entry

To edit, open the entry, tap **Edit**, change its fields, and tap **Save
credential**. **Cancel** discards the changes.

To delete, open the entry and tap **Delete**. In **Confirm deletion**, tap
**Cancel** to keep it or **Delete** to remove it. There is no undo or deleted-entry
recovery. Deleting a Lockbox entry does not delete the external account.

## Recover a forgotten master password

You need the existing vault on this phone and its saved recovery key.

1. On the login screen, tap **Forgot master password?**.
2. Enter the recovery key exactly as saved and tap **Continue**.
3. Enter and confirm a new master password meeting the same rules as setup.
4. Tap **Reset password**. Verification happens when you submit the reset;
   reaching the new-password screen does not by itself mean the key is valid.
5. On success the vault opens with its existing entries. Use the new master
   password for future logins; the previous one no longer unlocks it.

An incorrect key does not reset the password. The existing recovery key stays
valid after a successful reset. Older vaults may use a longer grouped key;
those legacy keys remain supported. Updating the app does not shorten them.

If both the master password and recovery key are lost, Lockbox cannot restore
access. There is no administrator or security-question bypass.

## Update the app

Obtain the intended newer APK from the maintainer and install it over the
existing app. Updates must have the same app identity and signing key to keep
the vault. Check that you can log in and that a saved test entry remains
after updating. Do not uninstall or clear data to resolve an installation
problem; those actions delete local vault data.

For computer-assisted installation and troubleshooting, see the
[deployment instructions](../release/installation-and-deployment.md).

## Troubleshooting

| Problem | What to do |
|---|---|
| Master passwords do not match | Re-enter both fields with identical capitalization and characters |
| Setup failed / password requirements | Check eight-character minimum and all four character categories; an existing vault cannot be initialized again |
| Unable to unlock vault | Check the master password; use recovery if forgotten |
| Recovery failed | Check the complete key and capitalization, then check the new master-password rules; verify both password entries match |
| Credential could not be saved | Fill in app/website name, username, and password; unlock again if the session expired |
| No credentials found | Clear the search or try part of the app/website name |
| Password will not copy | Open the entry and select Show password before Copy password |
| Keyboard hides a button | Scroll the form or dismiss the keyboard; report persistent problems with phone model and font setting |
| Screenshots/recording blocked | This is intentional protection for sensitive app content |
| App install/update fails | Check the APK, device compatibility and installation prompt; ask the maintainer about signing-key mismatches before uninstalling |
| App closes unexpectedly | Record the action and visible error and contact the maintainer; do not include passwords, recovery keys, or vault files |

## Current limits

Lockbox has no biometric unlock, autofill integration, browser extension,
cloud backup, synchronization, export/import, multi-user accounts, or
cross-device vault transfer. It cannot protect information already copied
into another app or keyboard history, or recover deleted vault data.
Screen-capture protection cannot stop an external camera or a compromised
device. Compatibility and accessibility have been tested only within the documented
project scope. See the [final test results](../testing/final-test-results.md)
for evidence and remaining gaps, and the [known limitations](../release/known-limitations.md)
for the consolidated register.
