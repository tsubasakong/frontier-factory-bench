"""Read project and compatibility metadata without third-party dependencies."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path

FLE_REVISION = (
    "factorio-learning-environment @ "
    "git+https://github.com/JackHopkins/factorio-learning-environment"
    "@6439e18b7870770454cf91eb36b3d1e6412724f4"
)


@dataclass(frozen=True, slots=True)
class CompatibilityMetadata:
    """The exact runtime compatibility boundary supported by this repository."""

    python_version: str
    requires_python: str
    factorio_version: str
    factorio_api_version: str
    fle_revision: str


COMPATIBILITY = CompatibilityMetadata(
    python_version="3.12.9",
    requires_python=">=3.12,<3.13",
    factorio_version="2.0.73",
    factorio_api_version="2.0",
    fle_revision=FLE_REVISION,
)


@dataclass(frozen=True, slots=True)
class RepositoryMetadata:
    """Metadata loaded from one repository checkout."""

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


def load_repository_metadata(root: str | Path) -> RepositoryMetadata:
    """Load version and compatibility files rooted at ``root`` using only stdlib."""

    repository_root = Path(root).resolve()
    with (repository_root / "pyproject.toml").open("rb") as file:
        pyproject = tomllib.load(file)
    with (repository_root / "mod/frontier_factory/info.json").open(encoding="utf-8") as file:
        mod_info = json.load(file)

    project = pyproject["project"]
    optional_dependencies = project.get("optional-dependencies", {})
    return RepositoryMetadata(
        project_name=project["name"],
        project_version=project["version"],
        requires_python=project["requires-python"],
        python_version=(repository_root / ".python-version").read_text(encoding="utf-8").strip(),
        factorio_version=(repository_root / "factorio-version").read_text(encoding="utf-8").strip(),
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
