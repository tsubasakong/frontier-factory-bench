#!/usr/bin/env python3
"""Check that repository version and compatibility sources agree."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PAYLOAD_PREFIX = "__FRONTIER_FACTORY_BENCH_METADATA__="
REPOSITORY_METADATA_FIELDS = (
    "project_name",
    "project_version",
    "requires_python",
    "python_version",
    "factorio_version",
    "default_dependencies",
    "integration_dependencies",
    "mod_name",
    "mod_version",
    "mod_factorio_version",
    "mod_dependencies",
    "hatch_allow_direct_references",
)
COMPATIBILITY_FIELDS = (
    "python_version",
    "requires_python",
    "factorio_version",
    "factorio_api_version",
    "fle_revision",
)

TARGET_METADATA_LOADER = f"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "src"))

try:
    import frontier_factory_bench as package

    package_path = Path(package.__file__).resolve()
    expected_package_root = (root / "src" / "frontier_factory_bench").resolve()
    if expected_package_root not in package_path.parents:
        raise ImportError(
            f"loaded {{package_path}} instead of a package below {{expected_package_root}}"
        )

    repository_metadata = package.load_repository_metadata(root)
    payload = {{
        "__version__": package.__version__,
        "compatibility": {{
            field: getattr(package.COMPATIBILITY, field)
            for field in {COMPATIBILITY_FIELDS!r}
        }},
        "repository": {{
            field: getattr(repository_metadata, field)
            for field in {REPOSITORY_METADATA_FIELDS!r}
        }},
    }}
except BaseException as error:
    print(f"{{type(error).__name__}}: {{error}}", file=sys.stderr)
    raise SystemExit(1) from error

print({PAYLOAD_PREFIX!r} + json.dumps(payload, sort_keys=True))
"""


class TargetPackageError(RuntimeError):
    """Raised when metadata cannot be read from the requested checkout's package."""


@dataclass(frozen=True, slots=True)
class RepositoryInputs:
    """Independently parsed metadata sources from one repository checkout."""

    canonical_version: str
    project_name: str
    project_version: str
    requires_python: str
    python_version: str
    factorio_version: str
    default_dependencies: tuple[str, ...]
    integration_dependencies: tuple[str, ...]
    mod_name: str
    mod_version: str
    mod_factorio_version: str
    mod_dependencies: tuple[str, ...]
    hatch_allow_direct_references: bool

    @property
    def factorio_api_version(self) -> str:
        return ".".join(self.factorio_version.split(".")[:2])


def _mismatch(label: str, actual: object, expected: object) -> str:
    return f"{label} is {actual!r}; expected {expected!r}"


def _load_repository_inputs(root: Path) -> RepositoryInputs:
    with (root / "pyproject.toml").open("rb") as file:
        pyproject = tomllib.load(file)
    with (root / "mod/frontier_factory/info.json").open(encoding="utf-8") as file:
        mod_info = json.load(file)

    project = pyproject["project"]
    optional_dependencies = project.get("optional-dependencies", {})
    return RepositoryInputs(
        canonical_version=(root / "VERSION").read_text(encoding="utf-8").strip(),
        project_name=project["name"],
        project_version=project["version"],
        requires_python=project["requires-python"],
        python_version=(root / ".python-version").read_text(encoding="utf-8").strip(),
        factorio_version=(root / "factorio-version").read_text(encoding="utf-8").strip(),
        default_dependencies=tuple(project.get("dependencies", ())),
        integration_dependencies=tuple(optional_dependencies.get("integration", ())),
        mod_name=mod_info["name"],
        mod_version=mod_info["version"],
        mod_factorio_version=mod_info["factorio_version"],
        mod_dependencies=tuple(mod_info.get("dependencies", ())),
        hatch_allow_direct_references=pyproject.get("tool", {})
        .get("hatch", {})
        .get("metadata", {})
        .get("allow-direct-references", False),
    )


def _load_target_package_metadata(root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-I", "-c", TARGET_METADATA_LOADER, str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (
            result.stderr.strip() or result.stdout.strip() or f"exit status {result.returncode}"
        )
        raise TargetPackageError(f"unable to import target package from {root / 'src'}: {detail}")

    payload_lines = [
        line.removeprefix(PAYLOAD_PREFIX)
        for line in result.stdout.splitlines()
        if line.startswith(PAYLOAD_PREFIX)
    ]
    if len(payload_lines) != 1:
        raise TargetPackageError(
            "target package metadata loader returned no unique metadata payload"
        )
    try:
        payload = json.loads(payload_lines[0])
    except json.JSONDecodeError as error:
        raise TargetPackageError(
            f"target package returned invalid metadata JSON: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise TargetPackageError("target package returned a non-object metadata payload")
    return payload


def _source_errors(inputs: RepositoryInputs) -> list[str]:
    errors: list[str] = []
    if not SEMANTIC_VERSION.fullmatch(inputs.canonical_version):
        errors.append(
            "VERSION must contain a three-component semantic version such as '0.0.0'; "
            f"found {inputs.canonical_version!r}"
        )

    comparisons = (
        ("pyproject project.name", inputs.project_name, "frontier-factory-bench"),
        ("pyproject project.version", inputs.project_version, inputs.canonical_version),
        ("mod info.json version", inputs.mod_version, inputs.canonical_version),
        ("pyproject default dependencies", inputs.default_dependencies, ()),
        ("Hatch direct-reference opt-in", inputs.hatch_allow_direct_references, True),
        ("mod info.json name", inputs.mod_name, "frontier_factory"),
        (
            "mod info.json factorio_version",
            inputs.mod_factorio_version,
            inputs.factorio_api_version,
        ),
        (
            "mod info.json dependencies",
            inputs.mod_dependencies,
            (f"base >= {inputs.factorio_version}",),
        ),
    )
    errors.extend(
        _mismatch(label, actual, expected)
        for label, actual, expected in comparisons
        if actual != expected
    )
    if len(inputs.integration_dependencies) != 1:
        errors.append(
            "pyproject integration extra must contain exactly one FLE direct reference; "
            f"found {inputs.integration_dependencies!r}"
        )
    return errors


def _public_metadata_errors(
    inputs: RepositoryInputs, package_metadata: dict[str, Any]
) -> list[str]:
    try:
        package_version = package_metadata["__version__"]
        compatibility = package_metadata["compatibility"]
        repository = package_metadata["repository"]
        if not isinstance(compatibility, dict) or not isinstance(repository, dict):
            raise TypeError("compatibility and repository values must be objects")
    except (KeyError, TypeError) as error:
        raise TargetPackageError(
            f"target package returned malformed public metadata: {error}"
        ) from error

    expected_repository: dict[str, object] = {
        "project_name": inputs.project_name,
        "project_version": inputs.project_version,
        "requires_python": inputs.requires_python,
        "python_version": inputs.python_version,
        "factorio_version": inputs.factorio_version,
        "default_dependencies": list(inputs.default_dependencies),
        "integration_dependencies": list(inputs.integration_dependencies),
        "mod_name": inputs.mod_name,
        "mod_version": inputs.mod_version,
        "mod_factorio_version": inputs.mod_factorio_version,
        "mod_dependencies": list(inputs.mod_dependencies),
        "hatch_allow_direct_references": inputs.hatch_allow_direct_references,
    }
    expected_compatibility: dict[str, object] = {
        "python_version": inputs.python_version,
        "requires_python": inputs.requires_python,
        "factorio_version": inputs.factorio_version,
        "factorio_api_version": inputs.factorio_api_version,
    }
    if len(inputs.integration_dependencies) == 1:
        expected_compatibility["fle_revision"] = inputs.integration_dependencies[0]

    comparisons: list[tuple[str, object, object]] = [
        ("package __version__", package_version, inputs.canonical_version)
    ]
    comparisons.extend(
        (
            f"package COMPATIBILITY.{field}",
            compatibility.get(field),
            expected,
        )
        for field, expected in expected_compatibility.items()
    )
    comparisons.extend(
        (
            f"package load_repository_metadata().{field}",
            repository.get(field),
            expected,
        )
        for field, expected in expected_repository.items()
    )
    return [
        _mismatch(label, actual, expected)
        for label, actual, expected in comparisons
        if actual != expected
    ]


def collect_version_errors(root: Path) -> tuple[str, ...]:
    """Return mismatches, including package metadata when the target package exists."""

    inputs = _load_repository_inputs(root)
    errors = _source_errors(inputs)
    if not (root / "src/frontier_factory_bench").is_dir():
        return tuple(errors)

    package_metadata = _load_target_package_metadata(root)
    return tuple(errors + _public_metadata_errors(inputs, package_metadata))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_ROOT,
        help="repository root to validate (defaults to the script's repository)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()

    try:
        inputs = _load_repository_inputs(root)
        package_metadata = _load_target_package_metadata(root)
        errors = tuple(_source_errors(inputs) + _public_metadata_errors(inputs, package_metadata))
    except TargetPackageError as error:
        print(f"Version metadata check failed: {error}", file=sys.stderr)
        return 1
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        tomllib.TOMLDecodeError,
    ) as error:
        print(
            "Version metadata check failed: unable to parse repository inputs "
            f"below {root}: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 1

    if errors:
        print("Version metadata check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Version metadata is consistent: {inputs.canonical_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
