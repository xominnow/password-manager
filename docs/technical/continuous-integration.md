# Continuous Integration

**Related checklist task:** 4.6  
**Status:** Configured; remote execution evidence recorded with task 9.9

GitHub Actions runs `.github/workflows/ci.yml` on pushes to `main` and on pull
requests. The workflow uses Python 3.13 and performs these checks:

1. Installs the pinned development dependencies.
2. Runs `pip check` for dependency consistency.
3. Compiles the `app/` and `tests/` Python sources.
4. Runs the pytest suite under Xvfb with software rendering on Ubuntu 24.04.

The UI regressions create real Kivy widgets. The runner installs Xvfb, Xauth,
Mesa/GL and libmtdev dependencies and sets `LIBGL_ALWAYS_SOFTWARE=1` and
`KIVY_NO_FILELOG=1`. A local Windows pass does not prove this Linux run passed;
see the [snapshot record](../release/final-source-snapshot.md) for evidence.

The workflow grants only read access to repository contents, cancels obsolete
runs for the same ref, and has a 15-minute timeout. Android packaging and
physical-device validation remain separate checks because they require the
WSL2/Buildozer environment and an Android test device.
