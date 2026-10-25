# Password Generation

**Related checklist task:** 6.6  
**Status:** Implemented in the security service layer; UI controls remain part of later Phase 6 integration.

`generate_password()` uses Python's `secrets` module, which delegates random
selection and shuffling to an operating-system cryptographically secure random
source. The default generated length is 20 characters, and callers may request
a longer or shorter value down to the approved eight-character minimum.

Every generated password contains at least one uppercase letter, lowercase
letter, number, and special character. The required category characters are
selected before the remaining characters, then the complete sequence is
securely shuffled. The generator rejects non-integer lengths, booleans, and
lengths below eight characters.

The generator returns the password to the caller for transient use. It does
not persist generated passwords or write them to logs.
