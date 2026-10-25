# Password-Strength Feedback

**Related checklist task:** 6.7  
**Status:** Implemented as an advisory service; UI presentation remains part of later Phase 6 integration.

`evaluate_password()` returns a small immutable `PasswordStrength` result with
a score from 0 to 4, a label, a policy-compliance flag, and human-readable
feedback. The result does not retain the original password, and the evaluator
does not log or persist it.

The feedback checks the approved minimum of eight characters and the presence
of uppercase, lowercase, numeric, and special characters. It also lowers the
advisory score for a short common-password list, repeated-character runs, and
recognizable ascending or descending sequences.

This evaluator is intentionally an interface aid rather than a cryptographic
security boundary. Generated passwords still use the dedicated CSPRNG-backed
generator, and the password policy remains enforced independently by the
credential and master-password workflows.
