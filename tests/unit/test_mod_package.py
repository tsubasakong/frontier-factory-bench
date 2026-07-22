import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SCRIPT = ROOT / "scripts/package_mod.py"


def _copy_packaging_inputs(destination: Path) -> None:
    destination.mkdir()
    for filename in (".python-version", "VERSION", "factorio-version", "pyproject.toml"):
        shutil.copy2(ROOT / filename, destination / filename)
    shutil.copytree(ROOT / "mod", destination / "mod")


def _run_packager(repository: Path, output_directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PACKAGE_SCRIPT),
            "--root",
            str(repository),
            "--output-dir",
            str(output_directory),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_mod_package_is_deterministic_and_has_the_factorio_layout(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    output_directory = tmp_path / "dist"
    _copy_packaging_inputs(repository)
    (repository / "mod/frontier_factory/.DS_Store").write_bytes(b"junk")
    bytecode_directory = repository / "mod/frontier_factory/__pycache__"
    bytecode_directory.mkdir()
    (bytecode_directory / "junk.pyc").write_bytes(b"junk")

    first_result = _run_packager(repository, output_directory)
    assert first_result.returncode == 0, first_result.stderr
    archive = output_directory / "frontier_factory_0.0.0.zip"
    first_digest = hashlib.sha256(archive.read_bytes()).hexdigest()

    second_result = _run_packager(repository, output_directory)
    assert second_result.returncode == 0, second_result.stderr
    second_digest = hashlib.sha256(archive.read_bytes()).hexdigest()

    assert second_digest == first_digest
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        assert [entry.filename for entry in entries] == [
            "frontier_factory_0.0.0/",
            "frontier_factory_0.0.0/data.lua",
            "frontier_factory_0.0.0/info.json",
        ]
        assert all(entry.date_time == (1980, 1, 1, 0, 0, 0) for entry in entries)
        packaged_info = json.loads(bundle.read("frontier_factory_0.0.0/info.json"))
        assert packaged_info["name"] == "frontier_factory"
        assert packaged_info["version"] == "0.0.0"


def test_mod_package_refuses_inconsistent_versions(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    output_directory = tmp_path / "dist"
    _copy_packaging_inputs(repository)
    (repository / "VERSION").write_text("0.0.1\n", encoding="utf-8")

    result = _run_packager(repository, output_directory)

    assert result.returncode == 1
    assert "version metadata is inconsistent" in result.stderr
    assert not output_directory.exists()


def test_mod_package_refuses_output_directory_inside_mod_source(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    _copy_packaging_inputs(repository)
    source_directory = repository / "mod/frontier_factory"
    output_directory = source_directory / "generated"

    result = _run_packager(repository, output_directory)

    assert result.returncode == 1
    assert "archive destination must not be inside mod source directory" in result.stderr
    assert not output_directory.exists()
    assert not list(source_directory.rglob("*.zip"))
    assert not list(source_directory.rglob("*.zip.tmp"))
