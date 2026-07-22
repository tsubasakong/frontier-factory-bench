import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_mod_info_has_the_minimum_base_factorio_schema() -> None:
    info = json.loads((ROOT / "mod/frontier_factory/info.json").read_text(encoding="utf-8"))

    required_types = {
        "name": str,
        "version": str,
        "title": str,
        "author": str,
        "factorio_version": str,
        "dependencies": list,
    }
    assert all(isinstance(info[field], expected) for field, expected in required_types.items())
    assert info["name"] == "frontier_factory"
    assert info["version"] == "0.0.0"
    assert info["factorio_version"] == "2.0"
    assert info["dependencies"] == ["base >= 2.0.73"]
