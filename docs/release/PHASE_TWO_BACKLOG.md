# Phase-Two Backlog

## Biometric unlock

**Status:** Deferred from phase one
**Priority:** Stretch goal
**Related checklist task:** 10.1

### Objective

Allow an authenticated user to unlock the local vault using Android biometric authentication while preserving the master-password security model.

### Required design constraints

- Use Android's platform biometric APIs through the approved Python-to-Android integration.
- Do not store biometric data in the application.
- Do not replace the master password as the primary vault-recovery method.
- Use Android Keystore-backed protection for any biometric unlock token or wrapped vault-key capability.
- Require the master password again after security-sensitive events, such as biometric enrollment changes or recovery-key reset.
- Provide a clear fallback to master-password login.
- Define behavior when the device has no enrolled biometric method.

### Future implementation tasks

1. Confirm Android API and Python bridge support.
2. Update the threat model and security design.
3. Define enrollment-change and lockout behavior.
4. Design biometric-specific UI states and error messages.
5. Implement Keystore-backed key protection.
6. Test success, failure, lockout, enrollment changes, and fallback login.
7. Update the user manual, technical documentation, and known limitations.

### Phase-one boundary

Biometric unlock is not part of the phase-one APK acceptance criteria and must not delay the October 21, 2026 submission.

