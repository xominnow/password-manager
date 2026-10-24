# Technology Stack Decision

**Project:** Android Password Manager
**Related checklist task:** 2.1
**Status:** Draft for review

## Decision summary

The project will use a Python-first Android stack. Kivy provides the mobile UI, Buildozer manages the Android build configuration, and python-for-android performs the underlying Android packaging. The application source will remain Python; Android platform APIs may be accessed through a Python bridge where required for secure-window behavior, clipboard handling, or future platform integration.

## Selected components

| Area | Decision | Role |
|---|---|---|
| Application language | Python | All application logic, security modules, storage logic, tests, and UI behavior. |
| UI framework | Kivy | Cross-device touch interface and screen/navigation implementation. |
| Android packaging | Buildozer | Main build configuration and APK build workflow. |
| Packaging backend | python-for-android | Cross-compiles Python and packages the app for Android. |
| Authenticated encryption | `cryptography` `AESGCM` | AES-256-GCM vault-record and wrapped-key encryption. |
| Password-based derivation | `cryptography` Scrypt KDF | Derives master and recovery key-encryption keys without an additional native package. |
| Secure randomness | Python `secrets` module | Generates vault keys, recovery keys, salts, and nonces. |
| Local database | Python `sqlite3` | Stores encrypted records and non-secret vault metadata locally. |
| Android API bridge | Python-to-Android bridge, to be confirmed during build setup | Accesses platform behavior not exposed directly by Kivy. |
| Automated tests | `pytest` | Unit and integration testing on the development environment. |
| Physical-device tests | Android Debug Bridge and manual test scripts | Installs and verifies the APK on a physical Android phone. |
| Build environment | Linux or WSL2 on Windows | Buildozer/python-for-android build environment. |

## Packaging path

```text
Python source + Kivy UI
          │
          ▼
Buildozer configuration
          │
          ▼
python-for-android toolchain
          │
          ▼
Debug APK for physical-device testing
```

The initial deliverable is a debug APK for private testing. Release signing and distribution controls are documented separately and are not treated as evidence of production certification.

## Python-only boundary

- No Kotlin or Java application source is planned.
- Android platform APIs may still be called through a Python bridge when necessary.
- Native Android dependencies must be documented and justified.
- If a dependency requires custom native code, the agent must stop and request approval before adding it.

## Build constraints

- Buildozer and python-for-android require a Linux or macOS build environment; on Windows, WSL is the planned route.
- The Android build must explicitly include only the dependencies required by the application.
- The build configuration must omit Internet permission unless a future approved requirement changes that decision.
- Dependencies and versions must be recorded and pinned or constrained before the first reproducible build.

## Security boundaries

- Kivy handles presentation, not cryptographic decisions.
- The security module owns key derivation, key wrapping, encryption, and authentication-tag validation.
- The storage module persists ciphertext and metadata, not plaintext secrets.
- Clipboard and secure-window integrations must have explicit tests because they cross the Python/UI and Android-platform boundary.

## Validation required before implementation lock

1. Confirm the selected Python and Kivy versions build under the chosen WSL environment.
2. Confirm the selected Scrypt implementation can be included by python-for-android.
3. Confirm the `cryptography` AESGCM dependency can be packaged for the target Android ABI.
4. Confirm the Android bridge needed for secure-window behavior.
5. Build and install a minimal Kivy APK on the physical test phone.

## Reference documentation

- Kivy Android packaging: https://kivy.org/doc/stable/guide/packaging-android.html
- Buildozer documentation: https://buildozer.readthedocs.io/en/stable/
- python-for-android documentation: https://python-for-android.readthedocs.io/en/develop/
- `cryptography` AES-GCM documentation: https://cryptography.io/en/stable/hazmat/primitives/aead/
- `cryptography` Scrypt documentation: https://cryptography.io/en/stable/hazmat/primitives/kdf/

