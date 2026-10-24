# Android Build Configuration

The first-machine commands below are historical setup notes, not a fully locked
clean-build recipe. For current commands/status use the
[deployment guide](../release/installation-and-deployment.md) and
[technical documentation](TECHNICAL_DOCUMENTATION.md). APK build, install and
device testing have since succeeded; release/source checksum equivalence remains
unverified. Use Windows ADB unless WSL USB passthrough is separately configured.

**Related checklist task:** 4.7  
**Status:** Draft for review

The initial Android packaging configuration is in `buildozer.spec`. It uses
Buildozer with python-for-android and the Kivy SDL2 bootstrap. The source root
is the repository root. The root `main.py` is the required
python-for-android launcher and delegates to `app.main.PasswordManagerApp`.

## Current packaging settings

- Application title: `Lockbox`
- Package name: `lockbox`
- Package domain: `com.xominnow`
- Version: `0.1.0`
- Orientation: portrait
- Minimum Android API: 26
- Target architectures: `arm64-v8a` and `armeabi-v7a`
- Runtime requirements: Python 3, Kivy 2.3.1, and cryptography 50.0.2
- python-for-android revision: `develop` at commit `0382d27`, which clears
  temporary build virtual environments and removes the failing pip self-upgrade
- Local p4a recipes: `p4a-recipes/cryptography` and `p4a-recipes/cffi`, which
  compile the native dependencies for Android using the selected API level
- Network permissions: none requested
- Presplash and icon: intentionally deferred until approved assets are available

## WSL2 build path

Buildozer is intended to run in WSL2/Linux rather than native Windows. The
first build machine setup should be performed in the project’s WSL2 checkout:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
  autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
  libtinfo5 cmake libffi-dev libssl-dev
sudo apt install -y rustup
rustup default stable
python3 -m venv .venv-buildozer
source .venv-buildozer/bin/activate
python -m pip install --upgrade pip
python -m pip install buildozer cython
buildozer android debug
```

For the current Rust-based `cryptography` and CFFI recipes, use the tracked
local recipes and pass the Android API level explicitly:

```bash
export ANDROID_API_LEVEL=26
buildozer android clean
env ANDROID_API_LEVEL=26 buildozer -v android debug 2>&1 | tee buildozer-build.log
```

The local recipes intentionally skip PyPI Android-wheel probing because these
packages must be compiled for the Android ABI. They use the controlled host
Maturin/build environment and `--no-isolation` instead of python-build's
isolated temporary pip environment, which is incompatible with the current
Python 3.14 host tooling.

The generated APK is expected under `bin/`. A connected test phone can be
used after enabling developer options and USB debugging:

```bash
adb devices
adb install -r bin/*.apk
```

The first build downloads Android tooling and can take substantial time. APK
creation, installation, launch, and device validation are separate acceptance
checks; this task only establishes the initial configuration.

## Packaging risks to verify

The cryptography requirement may require a Rust toolchain during the actual
python-for-android build. A successful Windows import does not prove that all
native Android recipes and wheels are available. Any failure must be recorded
as a release limitation and resolved before production claims are made.
