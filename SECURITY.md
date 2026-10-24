# Security Policy

## Project status

Lockbox is a capstone proof of concept under development. It must not be used
as a real password vault on the basis of capstone tests alone. Local tests and
user-reported device tests do not replace independent production security review.
The [security decisions](docs/architecture/security-decisions.md) and
[final test report](docs/testing/final-test-results.md) describe actual controls,
known limitations and incomplete evidence. Public debug APK distribution is approved.

## Reporting a vulnerability

Do not open a public issue containing exploitable details, credentials, vault
data, recovery keys, or other sensitive information. Use the repository's private
vulnerability-reporting option if enabled. Availability of a private reporting
channel has not been verified; if none is offered, ask the owner to establish
one without disclosing vulnerability details or secrets publicly. No response
time or long-term vulnerability-response service is promised by this prototype.

Include:

- A short description and impact
- Reproduction steps using synthetic test data only
- Affected commit or version
- Suggested mitigation, if known

Allow time for validation and remediation before public disclosure.

## Security requirements

- Never commit secrets or real credentials.
- Use established cryptographic libraries and approved parameters.
- Keep vault data local unless a future scope change is explicitly approved.
- Treat recovery keys and copied passwords as sensitive data. Keyboard history
  may retain copies; its remediation was explicitly skipped by the user.
- Record security-relevant limitations in the technical documentation.

See the [known-limitations register](docs/release/known-limitations.md) for
observed issues, excluded features and verification gaps. Its inclusion does
not turn unverified requirements into passes.
