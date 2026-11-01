# Agent notes

`obs-cli` is a Python command-line client for OBS Studio's WebSocket API v5.

- Preserve the command and output behavior documented in `README.md`.
- Run `python -m compileall -q obs_cli.py` for a local syntax check. No
  dedicated test suite is present.
- CI uses the shared
  [ci-workflows](https://github.com/pschmitt/ci-workflows) Python lint action.
- Before changing CI, check for a reusable workflow or action there and
  preserve the caller's existing behavior and check coverage.
- Do not validate state-changing commands against a personal OBS setup; use a
  disposable OBS test profile or a mock where integration coverage is needed.
- PyPI and GitHub release workflows run on version tags; ordinary development
  changes must not create tags.
