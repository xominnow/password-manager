# Application Shell and Navigation

**Related checklist task:** 4.3  
**Status:** Draft for review

The Kivy application entry point is `app/main.py`. It uses the shared product
settings for the application title and delegates screen registration to
`app/ui/navigation.py`.

## Navigation routes

`app/ui/navigation.py` defines the route names used by the presentation layer:

- `login`
- `setup`
- `recovery`
- `new_master`
- `vault`
- `entry`
- `detail`
- `generator`

Screens navigate through the centralized `Routes` constants rather than
duplicating string literals. The shell uses a short fade transition and starts
at setup for a new vault, or login for an existing vault. Authentication,
automatic locking, persistence, encryption and clipboard behavior are now
connected. See [current technical guide](TECHNICAL_DOCUMENTATION.md).
