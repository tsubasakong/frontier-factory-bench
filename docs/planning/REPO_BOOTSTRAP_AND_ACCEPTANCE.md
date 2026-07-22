# Repository bootstrap and acceptance plan

## Recommended repository identity

- **Planned owner:** `tsubasakong`
- **Repository name:** `frontier-factory-bench`
- **Planned repository slug:** `tsubasakong/frontier-factory-bench`
- **Creation status:** Public repository created on 2026-07-21; setup items below are completed incrementally by the numbered child issues.
- **Description:** Open benchmark for industrial agents operating modded Factorio production systems under automation, capacity, energy, and economic constraints.
- **Visibility:** Public
- **Code license:** MIT
- **Asset license:** CC BY 4.0 in a separate `LICENSE-ASSETS`, covering only project-original assets
- **Topics:** `factorio`, `llm-agents`, `reinforcement-learning`, `benchmark`, `industrial-automation`, `supply-chain`, `simulation`

`ASSET_PROVENANCE.md` must classify every distributed asset as `project-original`, `derived`, or `third-party`. CC BY 4.0 applies only to entries classified as `project-original`. Derived Factorio assets are excluded from both the MIT code license and `LICENSE-ASSETS`; they must identify their source and applicable Factorio terms. Third-party entries must identify their source and license. Development placeholders must be original generated color blocks, not extracted base-game graphics. `CONTRIBUTING.md` must preserve both the derived-asset exclusion and notice that distributing content as a Factorio mod may trigger the Wube Terms of Service grant-back provisions.

## Why an extension repository, not a fork

Use FLE as a pinned dependency and build a compatibility adapter around it. This preserves access to upstream headless execution, classic Gym integration, task infrastructure, and agent tooling while keeping the new domain independently versioned. The reviewed integration path is sufficient to keep the extension-repository/no-fork decision.

ADR-001 must record the following confirmed FLE v0.4.3 integration facts and decisions:

1. FLE v0.4.3 contains `attach_mod`/`FLE_MODS_PATH` code paths, but they are not connected to the generated container configuration.
2. The adapter owns the `factoriotools/factorio:2.0.73` container configuration, mounts this repository's mod and scenario directories, and connects FLE through `FACTORIO_SERVER_ADDRESS` and `FACTORIO_SERVER_PORT`.
3. FLE's hard-coded `Prototype` enum filters or rejects custom entities in core tools. The adapter supplies string-based placement, lookup, and observation tools instead of patching or mutating the enum at runtime.
4. The project self-registers its environment and constructs the FLE environment/task objects directly rather than relying on FLE's closed built-in task registry.

Runtime mutation of FLE's `Prototype` enum is prohibited in the formal acceptance path, including as a temporary fallback. If the string-based tools fail to place, inspect, or operate the required custom prototypes through a stable boundary, the vertical spike returns `NO-GO`; implementation stops before the full prototype chain or production art, and the project reopens the fork decision or requests a general-purpose upstream extension hook.

Adopt a fork only when one of these conditions is proven by the vertical spike:

1. The self-managed container and external environment registration path cannot support the required lifecycle without modifying FLE internals.
2. String-based tools cannot place, inspect, or operate custom prototypes through a stable public boundary.
3. Required observation or action extension points cannot be wrapped safely.
4. Upstream maintainers decline a small general-purpose extension hook and no maintainable adapter path remains.

## Pinned compatibility and version sources

The initial compatibility matrix is exact, not a floating `2.0.x` claim:

| Component | v0.1 pin | Policy |
|---|---|---|
| FLE | `v0.4.3`, commit `6439e18b7870770454cf91eb36b3d1e6412724f4` | Pin the tag and commit; upgrades require contract and end-to-end tests. |
| Factorio headless | `2.0.73` | Store this value in the root `factorio-version` single-source file. |
| Container image | `docker.io/factoriotools/factorio:2.0.73@sha256:6471fbfb7eab3abf55bb53fed632606ecf17bf930891bccddff724afab9ed94c` | Pin both tag and OCI index digest in local, CI, and release configuration. |
| Environment API | classic `gym` used by FLE v0.4.3 | Do not claim Gymnasium compatibility. |

Factorio `2.0.77` is a future upgrade candidate only. It does not enter the compatibility matrix until the spike, contract suite, packaged-mod smoke test, and end-to-end baselines pass against it.

Use a root `VERSION` as the project-version source and mechanically check that the Python package version, Factorio mod `info.json` version, package filename, and compatibility matrix agree. Commit `uv.lock` from day one and run `uv sync --locked` in CI.

Lightweight CI runs formatting, static checks, configuration validation, packaging checks, and unit/contract tests without Docker, Factorio, or API keys. Headless CI and `make smoke`, `make demo`, and `make benchmark` require Docker. Headless jobs use the tag-plus-digest image above. Do not commit or publish a Factorio binary. The official headless tarball, verified against Wube's published SHA-256 checksum, is a documented fallback only.

## Measurement and validity contract

The evaluator owns the holdout interval and records its start tick `t0`, end tick `t1`, and integer duration `window_ticks = t1 - t0`, where `window_ticks > 0`. The authoritative final-product counts for that interval are:

- `C_stats`: the integer delta of the real `compute-unit` item's per-surface production-statistics input count between `t0` and `t1`.
- `C_machine`: the integer sum, over eligible final-stage machines, of `delta(products_finished) * recipe_output_count` for the fixed compute-unit recipe.
- `C_ledger`: the integer delta of the mod-control completion ledger, incremented by the compute-unit recipe's actual output count on each eligible recipe completion.

A run is valid only when `C_stats = C_machine = C_ledger` exactly. These are integer counters, so no tolerance applies to this invariant. A direct production-stat mutation, scripted insertion, spawned output, or output-buffer movement cannot create a valid count unless the independent machine and mod-control completion sources agree; any mismatch marks the run invalid and records the specific violation.

For a valid run, sustained throughput is:

`throughput_units_per_minute = C_stats * 3600 / window_ticks`

because Factorio advances at 60 ticks per game-second. Input-consumption, energy, powered-state, and per-stage production measurements are diagnostics and plausibility signals, not independent hard-pass counters. Upstream buffers are legal, and holdout-time production at every upstream stage is not a hard pass condition; v0.1 evaluates valid sustained production of the final compute-unit stage.

## Suggested repository structure

```text
frontier-factory-bench/
├── .github/
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── assets/
│   ├── source/
│   ├── rendered/
│   └── ASSET_PROVENANCE.md
├── baselines/
├── benchmark/
│   ├── tasks/
│   ├── seeds/
│   └── scorecards/
├── docs/
│   ├── adr/
│   │   └── ADR-001-fle-integration.md
│   ├── compatibility.md
│   ├── glossary.md
│   ├── benchmark-card.md
│   └── roadmap.md
├── mod/
│   └── frontier_factory/
├── src/
│   └── frontier_factory_bench/
├── tests/
│   ├── unit/
│   ├── contract/
│   └── integration/
├── LICENSE
├── LICENSE-ASSETS
├── SECURITY.md
├── CONTRIBUTING.md
├── VERSION
├── factorio-version
├── pyproject.toml
├── uv.lock
├── README.md
└── Makefile
```

The to-spec issue itself should describe logical modules and contracts, not freeze these paths as permanent implementation decisions.

## Initial GitHub setup

The public repository was created at the confirmed slug on 2026-07-21. Complete and continuously verify the remaining setup:

1. Keep the public repository at `tsubasakong/frontier-factory-bench` free of generated application frameworks.
2. Add the MIT code license, CC BY 4.0 `LICENSE-ASSETS` limited to project-original assets, asset provenance policy, `SECURITY.md`, and contribution guide before accepting contributions.
3. Create the `ready-for-agent` label.
4. Add branch protection requiring lightweight CI; pin every referenced GitHub Action by full commit SHA and grant each workflow minimal permissions.
5. Enable dependency-update or dependency-audit automation for Python and GitHub Actions.
6. Add a spec issue template containing the to-spec headings.
7. Publish `SPEC_001_WALKING_SKELETON.md` as the first issue and apply only `ready-for-agent` as its triage label.
8. Add milestone `v0.1 — AI infrastructure walking skeleton`.
9. Split implementation work into child issues only after the parent spec is accepted.

## Recommended first child tasks

Each child task targets one to two working days and may be instantiated as a GitHub issue. Split a task before assignment if it cannot meet that bound. Dependencies are intentional; do not start the complete prototype chain or production art before Task 2 returns `GO`.

| Task ID | Child task | Depends on | Exit condition |
|---|---|---|---|
| 1 | Bootstrap Python packaging, `uv.lock`, version single sources, lightweight CI, security/license skeletons, and stable Make targets. | Accepted parent spec | `uv sync --locked` and `make test` pass without Docker or API keys. |
| 2 | Run the end-to-end de-risk spike for the custom mod/scenario, string-tool path, real recipe production, evaluator-owned holdout, three-count invariant, and first adversarial checks. | 1 | Every item in the machine-checkable Task 2 `GO` checklist below passes; publish ADR-001 and a documented `GO`. Any failed item returns `NO-GO`. No full prototype or production-art work starts before `GO`. |
| 3 | Prove the adapter contract and self-registered classic Gym entry point. Add project-owned contract tests for reset/step/close, the upstream `TaskABC.verify` signature mismatch, and FLE's missing Gym CI coverage. | 2 (`GO`) | `gym.make("FrontierFactory-AIInfra-v0")` works under the pinned set without the built-in FLE task registry. |
| 4 | Implement the complete quartz-to-compute prototype and recipe chain using placeholder original color-block art. | 2, 3 | All custom entities are placeable, observable, and operable through string-based tools. |
| 5 | Implement the fixed laboratory scenario, technology unlocks, deterministic reset subset, and versioned task configuration. | 4 | Repeated reset results agree on the documented state subset and tolerances. |
| 6 | Add original icons and principal machine/resource sprites, provenance entries, manifest lint, and packaged-mod validation. | 4 | The versioned mod zip has the required top-level structure and loads cleanly in the pinned image. |
| 7 | Implement evaluator state in private mod `storage`, the uniquely named read-only remote interface, and the complete action/code/result/error/tick log. | 4, 5 | Contract tests prove evaluator state is reset correctly, the agent-facing path cannot mutate it through the remote interface, and every submitted action has a complete ordered log record. |
| 8 | Implement the evaluator-owned tick holdout and the integer `C_stats = C_machine = C_ledger` validity invariant. | 7 | Holdout start/end barriers are deterministic, actions during holdout are rejected and logged, valid final-stage production yields three exactly equal integer counts, and any mismatch invalidates the run. |
| 9 | Add the passing and under-capacity scripted baselines. | 8 | The passing baseline exceeds the configured units/minute threshold with a valid three-count invariant; the under-capacity baseline remains below it and fails for `under-capacity`. |
| 10 | Add output-buffer, zero-action, disallowed-hand-craft, and action-during-holdout negative baselines. | 8 | Each baseline deterministically fails for its named reason; buffered output movement creates no valid holdout production, and the attempted holdout action is rejected and logged. |
| 11 | Add spawn, direct-insert, and stat-tampering adversarial baselines. | 8 | Spawned or directly inserted output cannot satisfy valid production, and direct production-stat mutation is marked invalid by an exact three-count mismatch with a specific violation. |
| 12 | Add end-to-end environment lifecycle, seeded task reset, and documented deterministic-subset/tolerance tests. | 3, 5, 9, 10, 11 | Fresh runs cover create/reset/step/verify/terminate/close; the seed and task configuration are exported; exact fields and tolerated fields repeat under their documented comparison rules. |
| 13 | Implement artifact export, checksums, release packaging, and a packaged clean-install smoke test. | 6, 12 | A fresh pinned container installs the versioned zip and emits schema-valid task config, versions, image digest, trajectory, raw counters, violations, logs, final-state reference, and verified checksums. |
| 14 | Write the benchmark card, reproducibility and security guidance, licensing notes, and the evidence-linked v0.1 release checklist. | 13 | Every v0.1 release gate has linked evidence or an explicit blocker; unresolved blockers prevent release. |

### Machine-checkable Task 2 `GO` checklist

Task 2 returns `GO` only when an automated spike test proves all of the following under the exact pinned compatibility set:

1. The repository-owned custom mod and custom scenario load in the self-managed container with no prototype or runtime errors.
2. String-based tools place and retrieve the custom machine without mutating FLE's `Prototype` enum.
3. The custom machine completes its real recipe and produces the real custom item.
4. During an evaluator-owned holdout, valid recipe production yields integer counts satisfying `C_stats = C_machine = C_ledger` exactly.
5. Moving pre-existing output from a buffer during holdout does not increase any valid production count and cannot satisfy throughput.
6. Scripted direct insertion of the output item does not increase the three valid production counts and cannot satisfy throughput.
7. Direct production-stat mutation causes a three-count mismatch, marks the run invalid, and records a tampering violation.
8. Any action attempted during holdout is rejected before execution and is recorded as an action-during-holdout violation.

Failure of any item is `NO-GO`. String-tool failure specifically prohibits enum mutation as a fallback and reopens either a FLE fork or a general-purpose upstream extension-hook proposal. Tasks 4 and 6, including the complete prototype chain and production art, remain blocked until `GO`.

## Milestones and objective acceptance

This document uses M0–M5. Earlier discussion treated the economic layer and supply shock as separate milestones; this plan consolidates both into M3, so later milestone numbers are shifted accordingly.

### M0 — Repository is agent-ready

**Deliverables**

- Public repository at the confirmed slug, code and asset licenses, contribution guide, `SECURITY.md`, glossary, ADR-001, spec template, `ready-for-agent` label, version single sources, committed `uv.lock`, lightweight CI, minimal mod package, and documented bootstrap/test/smoke commands.

**Acceptance**

- A fresh clone installs Python dependencies with one documented command using `uv sync --locked`.
- Formatting, static checks, configuration validation, package-structure checks, and unit/contract tests pass with no Docker, Factorio, or API keys.
- Docker is a documented prerequisite for `make smoke`, `make demo`, and `make benchmark`, but not for `make bootstrap` or `make test`.
- The first spec issue is present and follows the required headings.
- The compatibility matrix pins FLE v0.4.3 and its commit, Factorio 2.0.73, and the container tag plus digest exactly as specified above.
- The vertical spike passes every machine-checkable Task 2 `GO` condition: custom mod/scenario load; string-based custom-machine placement and retrieval; real recipe production; exact `C_stats = C_machine = C_ledger`; rejection of output-buffer movement and scripted direct insertion as valid production; invalidation of direct production-stat mutation by cross-check mismatch; and rejection plus logging of holdout actions.
- ADR-001 records the self-managed container, external FLE connection, string-tool layer, and no-fork decision. Any failed spike condition returns `NO-GO`, blocks M1, and reopens the fork or upstream-hook decision; runtime enum mutation is not an acceptance fallback.
- `make package` creates `frontier_factory_<VERSION>.zip` containing `frontier_factory_<VERSION>/info.json`; a clean pinned container installs and loads that zip without prototype or runtime errors.
- `SECURITY.md` states that agent-generated code is untrusted arbitrary Python and documents the v0.1 and public-leaderboard trust boundaries.
- Every referenced GitHub Action is pinned by full commit SHA, workflow permissions are minimal, and dependency-update/audit automation is configured.
- The asset manifest lint enforces `project-original`/`derived`/`third-party` classification and rejects project-license coverage for derived entries.
- No Factorio binary, proprietary base-game asset, token, or credential is committed.

### M1 — AI-infrastructure mod is playable

**Deliverables**

- The complete compact production chain, four principal machines, technology entries, localization, original icons and world sprites, and fixed scenario.

**Acceptance**

- Factorio 2.0.73 starts with the packaged mod enabled under the pinned image digest and produces no prototype or runtime errors.
- All required new prototypes can be enumerated through the game and string-based adapter tools.
- Every new item has a distinct original icon; all four principal machines and the quartz resource have visibly distinct original world sprites.
- The compute unit is a real item prototype; fluid and virtual-counter forms are rejected for v0.1.
- A human or deterministic setup script can produce at least one compute unit through the intended chain.
- Final-stage products cannot be completed by hand crafting; any allowed hand-craftable intermediates are an explicit allowlist.
- The simple acceptance run produces exactly equal integer `C_stats`, `C_machine`, and `C_ledger` counts.
- Asset provenance is complete, manifest lint passes, and the project asset license covers only entries classified as `project-original`.

### M2 — FLE environment contract works

**Deliverables**

- Self-registered classic Gym environment, reset/step/close support, string-based custom-prototype tools, structured observations, mod-storage task evaluator, read-only remote interface, baselines, and replay/log artifacts.

**Acceptance**

- `gym.make("FrontierFactory-AIInfra-v0")` creates the environment through the project's entry point under the pinned dependency set; the project does not claim Gymnasium compatibility.
- Project-owned contract tests cover reset/step return shapes, close behavior, task verification calls, the upstream `TaskABC.verify` signature inconsistency, and the Gym path omitted from upstream CI.
- `reset(seed=N)` returns a valid initial observation. Repeated resets with the same task configuration agree on a documented deterministic state subset; tick-sensitive or floating metrics use explicit tolerances instead of a blanket exact-hash claim.
- Public actions can inspect the new domain and construct and operate its machines through string-based tools without patching or mutating FLE's `Prototype` enum; failure of that path is `NO-GO`, not a runtime-enum fallback.
- Observations expose inventories, custom entities, research/technology state, per-surface production flows, task status, and actionable errors.
- The evaluator owns the holdout interval, rejects every agent action attempted during it before execution, records the violation, and measures the real compute-unit item's production delta over that window.
- The evaluator computes integer `C_stats`, `C_machine`, and `C_ledger` exactly as defined in the measurement contract. All three must be exactly equal or the run is invalid; throughput is `C_stats * 3600 / window_ticks` units per minute.
- Input consumption, energy, powered-state, and per-stage production are exported as diagnostics and plausibility signals. Upstream buffers are legal, and per-stage holdout production is not a hard pass condition.
- The evaluator's authoritative state lives in the mod's private `storage` and is exposed only through a read-only, uniquely named remote interface.
- Every submitted action/code block, result, error, and relevant game tick is logged.
- The passing baseline sustains the required throughput through the untouched verification window with a valid three-count invariant.
- The under-capacity, output-buffer, zero-action, disallowed-hand-craft, and action-during-holdout negative baselines each fail for their named reason.
- The spawn, direct-insert, and stat-tampering adversarial baselines fail or are marked invalid with a specific violation; production-stat tampering must be detected by an exact three-count mismatch.
- The run exports task configuration, seed, versions, image digest, trajectory, raw measurement sources, violations, logs, and final-state reference.

The formal posture is the **v0.1 cooperative-agent, audit-enforced threat model**: untrusted arbitrary Python is disclosed; the project relies on complete action logs, evaluator state in mod `storage`, a read-only remote interface, exact three-source measurement, and negative/adversarial baselines. It must not claim adversarial or public-leaderboard-grade isolation.

### M3 — Economic operations and supply shock

**Deliverables**

- Budget ledger, external procurement, spot prices, purchase-capacity limits, energy costs, compute revenue, deterministic event schedule, and one copper shock task.

**Recommended task**

`FrontierFactory-CopperShock-v0`: commission the data center, remain solvent, and restore at least 80% of pre-shock compute throughput within a defined recovery window after copper price and supply-capacity shocks.

**Acceptance**

- The same seed generates the same event schedule and price path.
- Market, cash, inventory valuation, capacity, and event state are observable through the public contract.
- Purchase, cancellation, and settlement rules are explicit and tested.
- The evaluator reports service level, compute throughput, uptime, revenue, procurement cost, energy cost, ending cash, profit, and recovery time.
- A no-adaptation policy performs materially worse than a shock-aware scripted baseline across the published seed set.
- Invalid arbitrage, negative-quantity orders, free inventory, duplicate settlement, and negative-price exploits are rejected.
- The benchmark clearly states that prices are stylized unless calibrated to cited external data.

### M4 — Reproducible benchmark release

**Deliverables**

- Versioned task suite, seed manifest, benchmark card, baseline results, release artifacts, compatibility matrix, security and licensing statements, and run comparison utility.

**Acceptance**

- A third party can reproduce the published scripted-baseline result from a fresh clone using documented commands and the pinned image.
- At least three baselines are reported: under-capacity/naive, deterministic competent, and one agent-driven reference run; adversarial/tampering checks are reported separately.
- Aggregate results include per-seed data rather than only averages.
- Success criteria, score formula, hard constraints, termination, time limits, measurement sources, deterministic tolerances, and known reward-hacking risks are documented.
- Release artifacts include the clean-install-tested mod package, Python package and lockfile, task definitions, seed manifest, checksums, result schema, licenses, and asset provenance manifest.
- The benchmark can be run without modifying source code to insert a new agent.

### M5 — Mars ISRU domain pack

**Deliverables**

- Water extraction, electrolysis, CO2 capture, methanation/Sabatier processing, oxygen and methane handling, liquefaction, rocket logistics, and a self-sufficiency task.

**Acceptance**

- The Mars task reuses the same public environment contract and evaluator framework.
- The resource loop is explicit: water supplies hydrogen and oxygen; atmospheric CO2 and hydrogen produce methane; oxygen and methane become propellant inputs.
- A closed-loop task measures imported mass, local propellant production, power demand, storage, launch readiness, and time to self-sufficiency.
- Scientific simplifications are documented and do not claim full engineering fidelity.

## v0.1 release gate

Do not call the project v0.1 until all of the following are true:

- One-command documented scripted demo from a fresh clone, with Docker prerequisites stated
- Exact FLE, Factorio, image tag/digest, Python, and mod versions recorded and mechanically checked for consistency
- `frontier_factory_<VERSION>.zip` contains `frontier_factory_<VERSION>/info.json` and passes a clean-install smoke test in the pinned image
- Public self-registered classic Gym environment and project-owned lifecycle/verification contract tests
- Deterministic reset documented as an explicit state subset with per-field exactness or tolerance, not an unspecified global hash
- Real compute-unit item measured by exact integer `C_stats = C_machine = C_ledger`, with throughput reported as `C_stats * 3600 / window_ticks` units per minute and input/energy/powered-state/per-stage data retained as diagnostics
- Passing baseline passes; under-capacity, output-buffer, zero-action, disallowed-hand-craft, and action-during-holdout negative baselines fail for their named reasons; spawn, direct-insert, and stat-tampering adversarial baselines fail or are marked invalid with specific violations
- Complete action/code log, task configuration, raw measurement sources, violations, versions, image digest, and final-state artifacts exported
- `SECURITY.md` documents arbitrary-Python risk, v0.1 controls, unsupported threat claims, and responsible reporting
- Supply-chain checks pass: locked Python dependencies, dependency audit/update policy, every referenced GitHub Action pinned by full SHA, and minimal workflow permissions
- MIT code license, CC BY 4.0 `LICENSE-ASSETS` limited to project-original assets, derived-asset exclusion and Wube grant-back notice in `CONTRIBUTING.md`, and complete `project-original`/`derived`/`third-party` asset provenance
- Asset manifest lint and release-time license/provenance review pass; placeholders and release assets contain no extracted proprietary base-game graphics
- No Factorio binary is stored in repository or release artifacts; any official-tarball fallback verifies Wube's SHA-256 checksum
- CI is green at lightweight and pinned headless integration levels
- Benchmark card states scope, non-goals, limitations, threat posture, deterministic tolerances, reward-hacking risks, and licensing

Full network and RCON isolation is not a v0.1 gate. v0.1 must describe the **v0.1 cooperative-agent, audit-enforced threat model** accurately and must not publish a public leaderboard under that model.

### Additional public leaderboard gate

Before accepting untrusted public submissions or publishing a leaderboard:

- Run agent, adapter, Factorio server, and evaluator in explicitly separated processes or containers with least-privilege users.
- Prevent the agent network namespace from reaching RCON or evaluator control ports and keep RCON credentials out of agent-readable files, environment variables, process arguments, and logs.
- Expose only an allowlisted action service to the agent; keep evaluator reads and holdout control on a private channel.
- Enforce evaluator-owned tick barriers and reject background or in-flight agent work during holdout.
- Prove with direct spawn, inventory insertion, production-stat mutation, credential discovery, and cross-run state-persistence baselines that tampering cannot produce a valid score.
- Re-run an independent security review of the pinned FLE/container boundary before leaderboard release.

## Suggested commands as user-facing contracts

The exact implementation may change, but preserve a small stable command surface:

```bash
make bootstrap   # install locked Python dependencies; Docker is not required
make test        # lightweight deterministic checks; no Docker or API key
make smoke       # package/load the mod and verify the environment; Docker required
make demo        # run the passing scripted baseline end to end; Docker required
make benchmark   # run the published seed suite; Docker required
make package     # build and validate mod and benchmark release artifacts
```

Scripted smoke, demo, and benchmark paths require no model-provider API key. Agent-driven reference runs may add provider-specific credentials without making them part of core acceptance.

## Main risks and mitigations

| Risk | Mitigation |
|---|---|
| FLE extension points change | Pin FLE tag and commit, own the container boundary, isolate the adapter, record ADR-001, and run project-owned contract tests. |
| Custom prototypes are rejected by FLE enums | Use tested string-based tools for placement, lookup, operation, and observation; do not mutate the enum at runtime. |
| Upstream classic Gym path drifts or remains untested | Self-register the entry point and test lifecycle return shapes plus task-verifier calls in this repository. |
| Scope expands into a full game | Freeze v0.1 to one chain, one environment, one passing baseline, and the accepted negative/adversarial baselines. |
| Art delays block research | Use original generated color-block placeholders after the integration spike; require only a small original sprite set for release. |
| Reward hacking through manual crafting, buffers, or statistic manipulation | Disable final hand crafting, use evaluator-owned holdout, compare three measurement sources, retain complete action logs, and run negative/tampering baselines. |
| Arbitrary agent Python reaches credentials or RCON | Disclose the v0.1 cooperative-agent, audit-enforced threat model; require process, credential, network, and allowlisted-action isolation before any public leaderboard. |
| Economic layer becomes arbitrary | Publish rules and raw metrics; label stylized parameters; later add optional calibrated profiles. |
| Non-reproducible environment | Pin FLE commit, Factorio version, image digest, seeds, event schedules, lockfile, deterministic subset/tolerances, and release checksums. |
| Proprietary asset or binary leakage | Use original art, tri-state provenance, manifest lint, release review, clean-package inspection, and no game binaries. |
| Supply-chain compromise | Lock dependencies, pin every referenced GitHub Action by full SHA, minimize workflow permissions, and automate dependency audits/updates. |
| Benchmark only tests memorized Factorio knowledge | Use a new technology tree, original nomenclature, hidden or held-out parameter variants, and seeded perturbations. |
| One model API becomes required | Keep scripted baselines and core acceptance completely provider-independent. |

## Confirmed decision (2026-07-21)

The following architectural seam is confirmed:

> The sole primary acceptance seam is the project's self-registered classic Gym/FLE environment lifecycle—create, reset, act, observe, verify, terminate, and export artifacts.

The mod-storage evaluator and read-only remote interface support that seam as internal trust and measurement mechanisms. They must not become a second agent-facing API. Everything else should support the primary seam rather than creating parallel public test interfaces.
