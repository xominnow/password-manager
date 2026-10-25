# Credential Viewing and Password Masking

**Related checklist task:** 6.2  
**Status:** Draft for review

`CredentialService.view()` authenticates and decrypts one stored entry only
when the vault session is unlocked. It returns a `CredentialView` whose
password is masked as `••••••••` by default.

The caller must explicitly call `reveal()` to obtain a displayable password and
may call `hide()` to return to the masked state. The view model excludes the
password from its default representation. Authentication or payload failures
produce a generic `CredentialReadError` and never return partial plaintext.

This task does not yet connect the view model to Kivy widgets or implement
editing and deletion.
