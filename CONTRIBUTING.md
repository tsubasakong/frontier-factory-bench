# Contributing

Thank you for contributing to Frontier Factory Bench. Changes should remain within the accepted walking-skeleton specification unless a new or amended spec is approved first.

## Prerequisites

The supported development runtime is:

- Python `3.12.9`;
- [`uv`](https://docs.astral.sh/uv/) for Python dependency and environment management;
- Docker only for `make smoke`, `make demo`, and `make benchmark`.

A local Factorio client, model-provider API key, and Docker are not required for `make bootstrap` or `make test`. Follow [docs/compatibility.md](docs/compatibility.md) rather than substituting newer dependency versions.

## Stable commands

Use the repository's public command surface:

```bash
make bootstrap   # install locked Python dependencies; no Docker or API key
make test        # run lightweight deterministic checks; no Docker or API key
make smoke       # package/load the mod and verify the environment; Docker required
make demo        # run the passing scripted baseline; Docker required
make benchmark   # run the published seed suite; Docker required
make package     # build and validate release artifacts
```

If a command is not implemented yet, keep the documented contract intact and link the missing implementation to its planned issue rather than inventing a competing command.

## Change process

1. Start from an issue with defined scope and acceptance criteria. Architecture or benchmark-semantics changes require a spec using the repository spec template.
2. Keep each pull request focused. Do not combine unrelated refactors, generated assets, dependency upgrades, and behavior changes.
3. Add or update tests at the public environment boundary when behavior changes. Record the exact commands and results in the pull request.
4. Update security, compatibility, licensing, and provenance documentation when the corresponding boundary changes.
5. Do not commit secrets, local credentials, generated run data containing secrets, or machine-specific configuration.
6. Ensure text files use LF endings and contain no trailing whitespace.

A submission is ready for review when its acceptance criteria are met, relevant tests pass, new dependencies and copied material are identified, and documentation reflects observable behavior. Compatibility claims must cite the exact pinned versions used for verification.

## Factorio binaries and graphics

Never commit or attach to a release:

- a Factorio executable, headless-server archive, or any other game binary;
- extracted or copied base-game graphics, textures, models, fonts, sounds, music, or other proprietary content;
- a container image that redistributes Factorio binaries;
- placeholders made by exporting, tracing, recoloring, or otherwise adapting base-game graphics without explicit review and provenance.

Use project-created source files and generated color-block placeholders. Runtime references to base-game prototype identifiers are distinct from copying base-game files, but they must still follow Factorio's modding rules.

## Asset provenance

Every asset under `assets/source/` or `assets/rendered/`, other than `.gitkeep`, must have exactly one entry in [assets/ASSET_PROVENANCE.md](assets/ASSET_PROVENANCE.md). Use one of the three manifest classifications:

- `project-original`: created specifically for this project by a contributor authorized to license it; covered by `LICENSE-ASSETS` when the manifest says `CC-BY-4.0`;
- `derived`: adapted from Factorio or another source; not covered by `LICENSE-ASSETS` and requires source-specific permission and maintainer review;
- `third-party`: obtained from an external creator without project adaptation; not covered by `LICENSE-ASSETS` and must retain its own source, author, attribution, and license terms.

Record the repository-relative `path`, `classification`, `source`, `author`, `license`, and any required attribution or modification details in `notes`. The pull request must update provenance in the same commit as the asset.

## Factorio terms and contributor notice

Factorio and its assets are owned by Wube Software Ltd. The current [Factorio Terms of Service](https://factorio.com/terms-of-service) state, among other things, that Wube retains rights in Factorio-derived assets and that distributing or publishing modifications or derivative works grants Wube a broad, irrevocable, perpetual, royalty-free, sublicensable license to those modifications or derivative works. Mod Portal uploads have additional terms.

By contributing content intended for distribution as part of the mod, you acknowledge that the Factorio Terms of Service may apply to that distribution. You must have authority to submit and license your contribution, and you must identify anything derived from Factorio or a third party. Project-original assets are licensed under `LICENSE-ASSETS`; derived and third-party assets remain under their applicable terms.

This guidance is a project policy summary, not legal advice. Contributors remain responsible for reviewing the applicable terms and obtaining legal advice when needed.

## Pull-request standard

Complete the pull-request template, including tests, security impact, dependency and license review, and asset provenance. A reviewer should be able to map each changed behavior to a requirement, an implementation, and evidence that the acceptance criterion passes.
