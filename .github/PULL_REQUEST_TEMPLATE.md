## Summary

Describe the outcome and why this change is needed.

## Linked issue and acceptance criteria

Link the issue or spec and map the implemented behavior to its acceptance criteria.

## Tests

List the exact commands run and their results. Explain any test that was not run.

- [ ] Relevant automated tests were added or updated.
- [ ] `make test` passes, or the exception is explained above.
- [ ] Docker-backed checks (`make smoke`, `make demo`, or `make benchmark`) were run when required, or are not applicable.
- [ ] Observable compatibility or reproducibility evidence is included when those contracts changed.

## Security

- [ ] Security impact was reviewed, including arbitrary Python, RCON, credentials, network access, evaluator state, and logs where relevant.
- [ ] No secret, credential, private trajectory data, or unsafe machine-specific configuration is included.
- [ ] Changes do not claim hostile-agent isolation or public-leaderboard readiness without satisfying the separate security gate.
- [ ] New dependencies, actions, images, and external inputs were reviewed and pinned as required, or are not applicable.

## License and provenance

- [ ] No Factorio binary or extracted/copied base-game graphic, model, font, sound, music, or other proprietary asset is included.
- [ ] New or changed dependencies and third-party material have compatible, documented licenses.
- [ ] Every added or changed asset has a complete `assets/ASSET_PROVENANCE.md` entry in the same change, or this pull request changes no assets.
- [ ] `project-original`, `derived`, and `third-party` classifications are accurate; `LICENSE-ASSETS` is applied only to `project-original` assets.
- [ ] Required author attribution, source links, modification notes, and Wube/third-party terms are preserved.

## Reviewer notes

Call out risk, follow-up work, compatibility caveats, or decisions that need particular attention.
