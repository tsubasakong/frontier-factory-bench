import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _copy_version_inputs(destination: Path) -> None:
    destination.mkdir()
    for filename in (".python-version", "VERSION", "factorio-version", "pyproject.toml"):
        shutil.copy2(ROOT / filename, destination / filename)
    shutil.copytree(ROOT / "mod", destination / "mod")
    shutil.copytree(
        ROOT / "src",
        destination / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def _run_version_check(repository: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/check_versions.py", "--root", str(repository)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_version_check_accepts_the_repository_metadata() -> None:
    result = _run_version_check(ROOT)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "Version metadata is consistent: 0.0.0\n"


def test_version_check_reports_every_source_that_drifted(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    _copy_version_inputs(repository)
    (repository / "VERSION").write_text("0.0.1\n", encoding="utf-8")

    result = _run_version_check(repository)

    assert result.returncode == 1
    assert "pyproject project.version" in result.stderr
    assert "package __version__" in result.stderr
    assert "mod info.json version" in result.stderr
    assert "expected '0.0.1'" in result.stderr


def test_version_check_detects_target_package_version_drift(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    _copy_version_inputs(repository)
    version_module = repository / "src/frontier_factory_bench/_version.py"
    version_module.write_text('__version__ = "9.9.9"\n', encoding="utf-8")

    result = _run_version_check(repository)

    assert result.returncode == 1
    assert "package __version__ is '9.9.9'; expected '0.0.0'" in result.stderr


def test_version_check_detects_target_compatibility_drift(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    _copy_version_inputs(repository)
    metadata_module = repository / "src/frontier_factory_bench/metadata.py"
    metadata_source = metadata_module.read_text(encoding="utf-8")
    metadata_module.write_text(
        metadata_source.replace('factorio_version="2.0.73"', 'factorio_version="2.0.74"'),
        encoding="utf-8",
    )

    result = _run_version_check(repository)

    assert result.returncode == 1
    assert "package COMPATIBILITY.factorio_version is '2.0.74'; expected '2.0.73'" in result.stderr


def test_version_check_reports_target_package_import_failure(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    _copy_version_inputs(repository)
    version_module = repository / "src/frontier_factory_bench/_version.py"
    version_module.write_text("this is not valid Python!\n", encoding="utf-8")

    result = _run_version_check(repository)

    assert result.returncode == 1
    assert "unable to import target package" in result.stderr
    assert "SyntaxError" in result.stderr


def test_version_check_reports_repository_parse_failure(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    _copy_version_inputs(repository)
    (repository / "pyproject.toml").write_text("[project\n", encoding="utf-8")

    result = _run_version_check(repository)

    assert result.returncode == 1
    assert "unable to parse repository inputs" in result.stderr
    assert "TOMLDecodeError" in result.stderr
