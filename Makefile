.DEFAULT_GOAL := help

UV ?= uv

.PHONY: help bootstrap check lint test package smoke demo benchmark

help:
	@printf '%s\n' \
		'Available targets:' \
		'  bootstrap  Install locked Python development dependencies (no Docker or API key)' \
		'  check      Verify project version consistency' \
		'  lint       Run Ruff lint and formatting checks' \
		'  test       Run version checks, lint, and pytest' \
		'  package    Build the Python and Factorio mod packages' \
		'  smoke      Reserved for Task 2+; currently returns an error' \
		'  demo       Reserved for Task 2+; currently returns an error' \
		'  benchmark  Reserved for Task 2+; currently returns an error'

bootstrap:
	$(UV) sync --locked --group dev

check:
	$(UV) run python scripts/check_versions.py

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

test: check lint
	$(UV) run pytest

package: check
	$(UV) build
	$(UV) run python scripts/package_mod.py

smoke demo benchmark:
	@printf '%s\n' "ERROR: make $@ is not implemented until Task 2+." >&2
	@exit 2
