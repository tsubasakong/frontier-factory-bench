from pathlib import Path

from frontier_factory_bench import COMPATIBILITY, __version__, load_repository_metadata

ROOT = Path(__file__).resolve().parents[2]


def test_public_metadata_matches_the_supported_repository_configuration() -> None:
    metadata = load_repository_metadata(ROOT)

    assert __version__ == "0.0.0"
    assert metadata.project_name == "frontier-factory-bench"
    assert metadata.project_version == "0.0.0"
    assert metadata.mod_name == "frontier_factory"
    assert metadata.mod_version == "0.0.0"
    assert metadata.hatch_allow_direct_references is True
    assert metadata.default_dependencies == ()
    assert metadata.integration_dependencies == (COMPATIBILITY.fle_revision,)
    assert COMPATIBILITY.python_version == "3.12.9"
    assert COMPATIBILITY.requires_python == ">=3.12,<3.13"
    assert COMPATIBILITY.factorio_version == "2.0.73"
    assert COMPATIBILITY.factorio_api_version == "2.0"
    assert COMPATIBILITY.fle_revision == (
        "factorio-learning-environment @ "
        "git+https://github.com/JackHopkins/factorio-learning-environment"
        "@6439e18b7870770454cf91eb36b3d1e6412724f4"
    )
