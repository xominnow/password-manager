# Project Documentation

This directory contains the project documentation required for the capstone submission.

## Documentation areas

- `requirements/` — functional and non-functional requirements
- `architecture/` — system architecture, threat model, and design decisions
- `database/` — database schema and storage design
- `ui/` — wireframes, mockups, and interface decisions
- `testing/` — test plan, test evidence, and test results
- `user-manual/` — installation and end-user instructions
- `technical/` — implementation and maintenance documentation
- `release/` — deployment instructions, release notes, and submission materials

## Project control

The [Lockbox user manual](user-manual/USER_MANUAL.md) provides installation,
setup, everyday use, recovery, and troubleshooting instructions.

The [technical documentation](technical/TECHNICAL_DOCUMENTATION.md) describes
the current implementation, module contracts, persistence, build and maintenance.

The [system diagrams](architecture/system-architecture.md),
[module architecture](architecture/application-architecture.md),
[database schema](database/schema.md), and
[database ER/review](database/DATABASE_DESIGN_REVIEW.md) describe the implemented design.

The [security decision register](architecture/security-decisions.md) records
security choices, user-approved exceptions, evidence and residual risks.

The [deployment guide](release/installation-and-deployment.md) covers APK
download, WSL builds, Windows ADB installation, checksums and updates;
[GitHub release instructions](release/github-release.md) cover public distribution.
The [final source/APK snapshot record](release/final-source-snapshot.md)
provides artifact identity and task 9.9 verification boundaries.

The [known limitations](release/known-limitations.md) register separates observed
issues, product/security constraints, deferred features and coverage gaps.

The [GUI evidence index](ui/SCREENSHOT_EVIDENCE.md) links the approved custom
mockups and nine clearly labeled synthetic desktop UI captures.

The authoritative progress tracker is the root-level [PROJECT_CHECKLIST.md](../PROJECT_CHECKLIST.md). Tasks are marked complete only after verification and the required user `PASSKEY`.

