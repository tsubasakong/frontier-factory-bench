#!/usr/bin/env python3
"""Build a deterministic, versioned Factorio mod archive."""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

from check_versions import collect_version_errors

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_DIRECTORIES = {".git", ".pytest_cache", ".ruff_cache", "__pycache__"}
EXCLUDED_FILENAMES = {".DS_Store", "Thumbs.db"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}


class PackagingError(RuntimeError):
    """Raised when repository state cannot produce a valid mod archive."""


def _is_packaged_file(path: Path, source_directory: Path) -> bool:
    relative_path = path.relative_to(source_directory)
    return not (
        any(part in EXCLUDED_DIRECTORIES for part in relative_path.parts)
        or path.name in EXCLUDED_FILENAMES
        or path.suffix in EXCLUDED_SUFFIXES
        or path.name.endswith("~")
    )


def _zip_entry(name: str, *, directory: bool) -> zipfile.ZipInfo:
    entry = zipfile.ZipInfo(name, date_time=FIXED_TIMESTAMP)
    entry.create_system = 3
    if directory:
        entry.compress_type = zipfile.ZIP_STORED
        entry.external_attr = (0o40755 << 16) | 0x10
    else:
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
    return entry


def _require_consistent_versions(root: Path) -> str:
    try:
        errors = collect_version_errors(root)
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
    except (FileNotFoundError, KeyError, OSError, TypeError, ValueError) as error:
        raise PackagingError(f"unable to read version metadata: {error}") from error

    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise PackagingError(f"version metadata is inconsistent:\n{details}")
    return version


def build_mod_archive(root: Path, output_directory: Path | None = None) -> Path:
    """Validate metadata and build the deterministic Factorio mod zip."""

    repository_root = root.resolve()
    version = _require_consistent_versions(repository_root)
    source_directory = (repository_root / "mod/frontier_factory").resolve()
    if not source_directory.is_dir():
        raise PackagingError(f"mod source directory does not exist: {source_directory}")

    destination = (output_directory or repository_root / "dist").resolve()
    if destination == source_directory or source_directory in destination.parents:
        raise PackagingError(
            "archive destination must not be inside mod source directory "
            f"(including the source directory itself): {destination}"
        )

    files = sorted(
        (
            path
            for path in source_directory.rglob("*")
            if path.is_file() and _is_packaged_file(path, source_directory)
        ),
        key=lambda path: path.relative_to(source_directory).as_posix(),
    )
    if not files:
        raise PackagingError(
            f"mod source directory contains no packageable files: {source_directory}"
        )
    if any(path.is_symlink() for path in files):
        raise PackagingError("mod source must not contain symbolic links")

    package_root = f"frontier_factory_{version}"
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"{package_root}.zip"
    temporary_archive = archive.with_suffix(".zip.tmp")

    with zipfile.ZipFile(temporary_archive, mode="w") as bundle:
        bundle.writestr(_zip_entry(f"{package_root}/", directory=True), b"")
        for path in files:
            relative_path = path.relative_to(source_directory).as_posix()
            bundle.writestr(
                _zip_entry(f"{package_root}/{relative_path}", directory=False),
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    temporary_archive.replace(archive)
    return archive


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_ROOT,
        help="repository root to package (defaults to the script's repository)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="archive destination (defaults to <root>/dist)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        archive = build_mod_archive(args.root, args.output_dir)
    except PackagingError as error:
        print(f"Mod packaging failed: {error}", file=sys.stderr)
        return 1

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(f"Built {archive} (sha256: {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
