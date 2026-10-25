[app]

# (str) Title of your application
title = Lockbox

# (str) Package name and domain
package.name = lockbox
package.domain = com.xominnow

# (str) Source code directory
source.dir = .
source.include_exts = py,kv,atlas,png,jpg,jpeg,svg,json
source.exclude_dirs = .git,.github,.venv,.venv313,docs,tests,scripts,bin,build,dist,.pytest_cache

# (str) Application version
version = 0.1.1

# (str) Application entry point
entrypoint = main.py

# (list) Application requirements
requirements = python3,kivy==2.3.1,cryptography==50.0.2
# Pin python-for-android to the merged fix for corrupted temporary pip venvs.
# This revision clears the build venv and removes the unsafe pip self-upgrade.
p4a.branch = develop
p4a.commit = 0382d27
p4a.local_recipes = p4a-recipes

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# (str) Android application format
android.archs = arm64-v8a,armeabi-v7a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (int) Minimum Android API level; matches the approved Android 8.0/API 26 baseline
android.minapi = 26

# (str) Android entry activity
android.entrypoint = org.kivy.android.PythonActivity

# (str) Presplash and icon are intentionally omitted until approved assets exist.
# presplash.filename = %(source.dir)s/data/presplash.png
# icon.filename = %(source.dir)s/data/icon.png

# (str) Custom build directory location
# Use a project-local build directory for current Buildozer config parsing.
build_dir = .buildozer

# (str) Output directory for generated APK/AAB files
bin_dir = ./bin

# (str) Log level
log_level = 2
