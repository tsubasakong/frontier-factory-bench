"""Public metadata interface for Frontier Factory Bench."""

from ._version import __version__
from .metadata import COMPATIBILITY, CompatibilityMetadata, RepositoryMetadata
from .metadata import load_repository_metadata as load_repository_metadata

__all__ = [
    "COMPATIBILITY",
    "CompatibilityMetadata",
    "RepositoryMetadata",
    "__version__",
    "load_repository_metadata",
]
