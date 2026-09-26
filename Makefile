UV := .tools/uv-0.12.19/uv

.PHONY: sync python_workspace_smoke format format-check lint type-check unit-test

sync:
	$(UV) sync --frozen --all-packages

python_workspace_smoke:
	$(UV) run --frozen pytest -q tests/test_python_workspace.py -k python_workspace_smoke

format:
	$(UV) run --frozen ruff format apps packages tests/test_python_workspace.py

format-check:
	$(UV) run --frozen ruff format --check apps packages tests/test_python_workspace.py

lint:
	$(UV) run --frozen ruff check apps packages tests/test_python_workspace.py

type-check:
	$(UV) run --frozen mypy apps packages tests/test_python_workspace.py

unit-test:
	$(UV) run --frozen pytest
