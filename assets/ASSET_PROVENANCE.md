# Asset Provenance Manifest

This file is the authoritative manifest for project asset provenance. Every file under `assets/source/` and `assets/rendered/`, excluding `.gitkeep`, must appear exactly once. Paths are repository-relative POSIX paths and are case-sensitive.

## Machine-readable manifest

```yaml
schema_version: 1
assets: []
```

There are currently no asset entries.

Each future `assets` entry must contain all of these scalar fields:

| Field | Required content |
| --- | --- |
| `path` | Unique repository-relative path under `assets/source/` or `assets/rendered/`. |
| `classification` | Exactly one of `project-original`, `derived`, or `third-party`. |
| `source` | Creation source, repository source path, or canonical external URL. |
| `author` | Person or organization that created the asset. |
| `license` | SPDX identifier where available, otherwise the exact governing terms and URL. |
| `notes` | Attribution, modifications, generation method, exclusions, or `none`. |

## Classification rules

- `project-original` is the project's original-asset class. The contributor must have authority to license the work. `LICENSE-ASSETS` applies only when an entry has this classification; use `CC-BY-4.0` in `license` unless an approved exception is documented.
- `derived` covers adaptations of Factorio assets or any other pre-existing material. It is not covered by `LICENSE-ASSETS`. Record the original source, rights holder, governing permission, and modifications. Derived assets require maintainer review before inclusion.
- `third-party` covers externally created material distributed without a project adaptation. It is not covered by `LICENSE-ASSETS`. Record the canonical source, author, exact license, and required attribution.

Do not add extracted Factorio graphics as source material or placeholders. A manifest entry documents provenance; it does not create permission that the contributor or project does not possess.
