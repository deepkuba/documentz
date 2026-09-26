# Use CPython 3.14 and uv for the Python workspace

Documentz will support CPython 3.14, pin 3.14.7 for development and CI, and use uv 0.12.19 for Python installation, workspace dependency resolution, and the checked-in universal lockfile. Ruff 0.16.9 provides formatting and linting, mypy 2.3.1 provides static type checking, and pytest 9.1.1 provides tests. This keeps bootstrap and locking in one tool while retaining dedicated, widely supported quality tools; Python 3.14 receives upstream support through October 2030 and every selected tool supports it.

Compatibility evidence (checked 2026-09-26): [Python support lifecycle](https://www.python.org/downloads/), [uv Python support policy](https://docs.astral.sh/uv/reference/policies/python/), [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/), [Ruff package](https://pypi.org/project/ruff/0.16.9/), [mypy package](https://pypi.org/project/mypy/2.3.1/), and [pytest package](https://pypi.org/project/pytest/9.1.1/).
