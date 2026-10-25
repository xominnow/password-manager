# Python Development Environment

**Project:** Android Password Manager
**Related checklist task:** 4.1
**Status:** Draft for review

Current deployment reference: [installation and deployment](../release/installation-and-deployment.md).
Windows tests now use `.venv313` with Python 3.13.17. The initial global/.venv
observations below are historical. WSL's existing build environment is separate;
its Python 3.14 compatibility work is handled by the documented local recipes.

## Observed environment

- Windows development host
- Python 3.15.1 is installed globally and in the existing `.venv`.
- Python virtual environment at `.venv`
- pip 26.2.2 in the virtual environment

The initial Python 3.15 environment failed to install the Windows Kivy dependencies.
Use the verified Python 3.13 Windows test environment. Do not assume the Windows
version or virtual environment can be reused inside WSL: preserve the separately
configured Buildozer environment and record its actual toolchain versions.

## PowerShell setup

From the project root:

```powershell
py -3.13 -m venv .venv313
.\.venv313\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If the environment already exists, activate it and install from the same manifest:

```powershell
.\.venv313\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Verification commands

```powershell
python --version
python -m pip --version
python -c "import kivy, cryptography; from cryptography.hazmat.primitives.kdf.scrypt import Scrypt; print('runtime dependencies import successfully')"
python -c "import ast, pathlib; files=(pathlib.Path('app/main.py'), pathlib.Path('app/ui/screens.py')); [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print('UI syntax check passed')"
pytest -q
```

The import and test commands should be run only after dependencies are installed. Do not place passwords, recovery keys, vault files, or signing keys in the virtual environment or repository.

## Android build environment

Native Windows Python is sufficient for host-side syntax and unit checks. APK packaging will use WSL2/Linux with Buildozer and python-for-android. The WSL runtime version and installed system packages will be recorded during the Android build-configuration task.

## Dependency policy

- Runtime and development dependencies are separated into two manifests.
- Version ranges are constrained for compatibility review.
- Exact resolved versions will be recorded after the first successful installation and build validation.
- Dependency upgrades require rerunning security, import, test, and packaging checks.

