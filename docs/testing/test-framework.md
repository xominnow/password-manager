# Test Framework

**Related checklist task:** 4.4  
**Status:** Draft for review

The project uses `pytest`. Test discovery is configured in `pytest.ini` and
currently targets the `tests/` directory.

The initial tests cover centralized security defaults and route definitions.
They intentionally avoid starting a graphical Kivy window so they can run on
Windows development hosts and in headless CI environments. UI behavior,
cryptography, storage, Android packaging, and device testing will be added as
their corresponding features are implemented.

Run the current suite from the project root with:

```powershell
pytest -q
```
