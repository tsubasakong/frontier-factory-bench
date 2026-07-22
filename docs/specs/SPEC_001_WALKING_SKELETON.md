# [SPEC] AI infrastructure walking skeleton

Suggested GitHub label: `ready-for-agent`

## Problem Statement

As an agent-environment researcher, I need a small but complete proof that a new, visually distinct industrial technology tree can run inside Factorio and be evaluated through the Factorio Learning Environment contract. Without that vertical slice, the project risks spending substantial effort on art, economics, space systems, and reinforcement-learning infrastructure before validating the core integration.

The proof must demonstrate the entire loop: the mod loads, the new domain is visible, an agent can observe and manipulate it, the environment can reproducibly reset, a production objective can be scored from external behavior, and a baseline can complete the objective without private evaluator access.

## Solution

Create a base-Factorio-compatible mod and FLE extension that introduces a compact AI-infrastructure production chain:

- quartz ore
- purified silicon
- silicon wafer
- AI accelerator
- server rack
- data-center node
- `compute-unit` as a real, storable item and the benchmark output

Provide original icons for every new item and technology, original world sprites for the principal machines, and original stage sprites for the quartz resource. Register one classic `gym` environment, `FrontierFactory-AIInfra-v0`, with a fixed laboratory-style starting scenario. The task is complete when the agent constructs an automated chain that sustains the required compute-unit throughput during an evaluator-owned verification window.

Ship a reproducible scripted baseline and an end-to-end acceptance test through the public environment interface.

## User Stories

1. As an agent researcher, I want to create the benchmark through a standard classic `gym` environment identifier, so that I can use existing evaluation harnesses.
2. As an agent researcher, I want the adapter and scenario to implement reproducible reset by seed, so that runs can be compared despite FLE 0.4.3 ignoring the public `reset(seed=...)` argument.
3. As an agent developer, I want observations to identify the new resources, items, recipes, technologies, entities, inventory, production flows, and task status, so that my agent can reason about the domain.
4. As an agent developer, I want to use the existing FLE code-action model, so that I do not need a separate mouse-and-keyboard controller.
5. As an agent developer, I want clear errors when I request an unavailable recipe, invalid entity, impossible placement, or missing ingredient, so that the agent can recover.
6. As an agent, I want to mine or receive quartz ore, so that I can begin the semiconductor chain.
7. As an agent, I want to purify silicon, so that I can produce wafer-grade material.
8. As an agent, I want to fabricate silicon wafers, so that I can produce AI accelerators.
9. As an agent, I want to combine wafers with conventional Factorio intermediates, so that the new domain remains connected to the base-game production system.
10. As an agent, I want to assemble AI accelerators, so that I can advance to server hardware.
11. As an agent, I want to assemble server racks, so that I can commission data-center capacity.
12. As an agent, I want a data-center node to consume electricity, server racks, and other inputs while emitting measurable compute units, so that the final objective represents an operating system rather than a one-time craft.
13. As an evaluator, I want success to require production during an evaluator-owned holdout window, so that moving prebuilt output cannot falsely satisfy the objective.
14. As an evaluator, I want final-stage products to be non-hand-craftable and the hand-craft exception list to be explicit, so that the benchmark measures automation rather than manual crafting.
15. As an evaluator, I want decomposed raw metrics for every production stage, power, action quality, cost, automation validity, elapsed ticks, and completion, so that failures are diagnosable.
16. As a benchmark maintainer, I want one scripted baseline to pass from a clean reset, so that CI can prove the task remains solvable.
17. As a benchmark maintainer, I want insufficient and adversarial baselines to fail, so that the verifier is shown to reject both weak factories and metric manipulation.
18. As a benchmark maintainer, I want the same seed and action sequence to reproduce the task result and a documented metric subset within declared tolerances, so that regressions can be detected without promising full-world tick-for-tick identity.
19. As a mod player, I want new items and machines to be visually distinguishable from base-game content, so that the project visibly communicates the AI-infrastructure theme.
20. As an art contributor, I want every asset to have source and license metadata, so that the repository can be redistributed safely.
21. As a code contributor, I want the mod, adapter, tasks, evaluator, and baselines to be logically separated, so that changes have clear ownership.
22. As a task author, I want task configuration to be declarative where practical, so that later variants can reuse the same domain implementation.
23. As a maintainer, I want FLE-specific behavior isolated behind a compatibility boundary, so that an upstream FLE upgrade does not require rewriting the domain mod.
24. As a maintainer, I want the exact Factorio, FLE, and container versions recorded, so that installation and behavior changes are attributable.
25. As a new contributor, I want a single documented demo command, so that I can see the complete benchmark loop before learning the internals.
26. As a CI operator, I want unit checks to run without model API keys, so that pull requests are inexpensive and reproducible.
27. As a CI operator, I want the heavier headless-Factorio smoke test to be separately invokable, so that it can run on protected branches, nightly, and before releases.
28. As a researcher, I want trajectories, submitted code, and evaluator outputs to be saved as artifacts, so that I can inspect why a run passed or failed.
29. As a future task author, I want the AI-infrastructure chain to be reusable by economic-shock tasks, so that v0.2 does not duplicate prototypes or recipes.
30. As a future domain author, I want the architecture to permit a Mars ISRU pack without changing the public agent-environment contract, so that the benchmark can expand coherently.

## Implementation Decisions

- The repository identity is `tsubasakong/frontier-factory-bench`. It is an independent repository that depends on a fixed FLE revision rather than forking FLE initially.
- The first mod depends only on base Factorio 2.0. Space Age, Quality, and Elevated Rails are not required.
- The domain is a normal Factorio mod: prototypes and recipes are defined during the data stage; evaluator timing, task state, and runtime integration are defined during the control stage.
- The Factorio mod, Python compatibility adapter, task definitions, evaluator, baselines, tests, assets, and documentation live in one monorepo but remain separate logical modules.
- The public agent interaction remains the FLE code-action contract. The project does not add a second action protocol in v0.1.
- The public environment lifecycle remains `reset`, `step`, and `close`, with structured observations, scalar reward, termination flags, and structured information. Compatibility means classic `gym` as used by FLE 0.4.3, not Gymnasium.
- The canonical environment identifier is `FrontierFactory-AIInfra-v0`.
- The starting scenario is laboratory-style and selected by adapter-owned seed semantics. It supplies a controlled map, required base resources, a quartz patch, and enough starting capability to avoid unrelated early-game survival work.
- Quartz is placed by the benchmark scenario; v0.1 does not require general-purpose quartz world generation.
- The production chain is quartz ore → purified silicon → silicon wafer → AI accelerator → server rack → data-center node → compute unit. Server racks are a low-rate recurring consumable in compute production, so they remain a replenishable operating input rather than one-time construction material. v0.1 does not require every upstream stage to run during the same holdout.
- Base-game intermediates such as copper products, steel, circuits, plastic, electricity, water, sulfuric acid, and lubricant may connect the new chain to existing automation. The wafer recipe should use sulfuric acid.
- AI accelerator, server rack, and compute-unit recipes use dedicated machine-only recipe categories with `hide_from_player_crafting = true` and `allow_as_intermediate = false`. The only benchmark-added recipe on the character hand-craft allowlist is purified silicon; quartz may be hand-mined, while wafers and all later products require machines.
- The data-center node uses a `fixed_recipe`, explicit `energy_usage` and idle `drain`, and no module slots. Compute-unit output may be stored in v0.1, but inventory levels never contribute to task success.
- Principal machines have original world sprites. Every new item and technology has an original icon, and quartz has original resource-stage sprites. All new content has localized display text.
- No LLM API call is required for installation, CI, scripted baselines, or acceptance testing.
- The repository contains no Factorio executable, base-game graphics, or credentials. Project assets include provenance and license records; code and original visual assets use separately recorded compatible licenses.

## Compatibility Boundary

The first supported matrix row is fixed as follows:

| FLE | FLE commit | Factorio | Container tag | OCI index digest | Content |
| --- | --- | --- | --- | --- | --- |
| `v0.4.3` | `6439e18` | `2.0.73` | `docker.io/factoriotools/factorio:2.0.73` | `sha256:6471fbfb7eab3abf55bb53fed632606ecf17bf930891bccddff724afab9ed94c` | base only |

- The adapter owns container orchestration and mounts project-owned mod and scenario directories. FLE connects to the running server through `FACTORIO_SERVER_ADDRESS` and `FACTORIO_SERVER_PORT`.
- The adapter does not rely on FLE 0.4.3's unconnected `attach_mod` or `FLE_MODS_PATH` paths.
- The repository calls `gym.register` itself. Its entry point directly constructs `FactorioGymEnv(instance, task)` using a project-created `FactorioInstance` and `TaskABC` subclass, bypassing the closed upstream task registry.
- Adapter tests cover classic `gym` behavior, the effective `verify` call signature, and environment lifecycle because FLE 0.4.3's upstream CI does not exercise its gym suite.
- FLE's hard-coded Python `Prototype`, `RecipeName`, and related enums do not recognize new entities reliably and may filter them from observations. The adapter therefore provides string-accepting project tools, preferably through a project-owned `FLE_TOOLS_DIR` tool set. Runtime enum injection is forbidden in the formal acceptance path. If the string-tool path fails, the spike is `NO-GO` and the project must reopen the fork or upstream-extension-hook decision.
- A compatibility contract test must place and retrieve a custom entity, set or inspect its recipe, and observe custom inventory through the public adapter.
- FLE 0.4.3 ignores `reset(seed=...)`; the adapter and scenario implement seed selection and clean-state reconstruction. Upgrades require the full acceptance suite to pass before this matrix changes.

## Measurement Contract

- `compute-unit` is a real item. The holdout is owned and timed by mod control using `game.tick`. Before tick `t1`, the evaluator establishes a barrier, freezes the tracked data-center-node set, and snapshots counters. From `t1` through `t2`, agent API calls are rejected and recorded as violations.
- `C_stats` is the integer delta over the holdout of `force.get_item_production_statistics(surface).get_input_count("compute-unit")` on the configured surface.
- `C_machine` is the integer sum, over tracked data-center nodes, of `delta(products_finished) * compute-unit recipe output quantity`.
- `C_ledger` is the integer completion ledger maintained in mod `storage`. Mod control observes each `products_finished` increment every tick, or by deterministic polling that cannot miss a completion, verifies that the source is a valid tracked entity running the fixed compute-unit recipe, and adds the corresponding recipe output quantity.
- A valid run requires the exact integer invariant `C_stats == C_machine == C_ledger`. Any mismatch makes the run invalid. Passing additionally requires `C_stats * 60 * 60 / (t2 - t1)` to meet or exceed the configured quota in units per minute. The task configuration defines the surface, `t2 - t1` holdout ticks, and quota.
- v0.1 requires sustained, genuine final-stage production by data-center nodes during the holdout. Legal upstream input buffers are allowed; per-stage throughput remains diagnostic, and no upstream stage is required to produce during that same window. Server racks remain recurring consumables so the chain must be replenishable over longer operation.
- Output inventory snapshots do not contribute to success. Moving prebuilt compute units or adding them through scripted `insert` does not increment the production statistic. Upstream-buffer inventory is allowed.
- Required-input consumption and power or energy samples are retained as diagnostics and plausibility checks, not as undefined exact-equality sources. A production count above the theoretical maximum implied by the fixed recipe, fixed crafting speed, and elapsed powered crafting ticks makes the run invalid. The documented and tested bound may allow at most one in-progress carry-in craft per tracked machine at `t1`.
- Reproducibility means equal completion status plus a documented subset of raw metrics within declared tolerances for the same seed and action sequence. The benchmark does not promise a full-world, per-tick hash match.
- Raw metrics are reported before any aggregate score: final and per-stage throughput, holdout duration, machine uptime, power satisfaction and energy use, elapsed ticks, action errors by category, entity and resource cost, automation violations, cross-check deltas, and completion status.
- Automation violations use a closed set for each task-schema version, with versioned extensions allowed. The initial set is `disallowed_hand_craft`, `action_during_holdout`, `spawn_or_stat_tampering`, and `evaluator_interface_misuse`.

## Threat Model

The formal model is the **v0.1 cooperative-agent, audit-enforced threat model**. Every submitted action and code payload is logged. Evaluator state lives in the benchmark mod's private `storage` and is exposed only through a read-only, uniquely named remote interface. The pass decision enforces the exact `C_stats == C_machine == C_ledger` invariant rather than trusting one FLE statistic; input and energy data remain diagnostic plausibility evidence.

FLE code actions may still reach privileged Lua, including production-statistic mutation such as `set_flow_count`; v0.1 therefore detects and rejects known manipulation through logs, cross-checks, and a mandatory spawn/stat-tampering adversarial baseline. It does not claim containment against a hostile process with direct RCON, network, filesystem, or host access. Isolated agent networking, inaccessible RCON credentials, and an allowlisted server action surface are mandatory before any public leaderboard or untrusted-agent service.

## Testing Decisions

- The primary test seam is the public environment boundary: register the environment, reset it, submit actions, inspect observations, evaluate the task, and close it. Internal Lua and Python details are secondary seams.
- The end-to-end test follows one complete trajectory through classic `gym.make`, adapter-owned seeded reset, repeated `step`, evaluator-owned holdout, termination, cleanup, and artifact export.
- The Factorio mod is tested for externally observable load success: all required prototypes exist, recipes and technologies are valid, the scenario starts, and target machines operate.
- The compatibility adapter is tested for self-managed container startup, external FLE connection, environment registration, string-based custom prototype actions and observations, error propagation, reset behavior, and cleanup.
- Evaluator baselines include a passing scripted factory that must pass and the following cases that must fail or be marked invalid for their intended reason: under-capacity, buffer-only, spawn/stat-tampering, disallowed-hand-craft, action-during-holdout, and zero-action.
- Reproducibility is tested by replaying the same seed and action sequence and comparing completion status and the documented metric subset under declared tolerances.
- Asset checks cover item and technology icons, machine sprites, quartz resource-stage sprites, dimensions, identifiers, alpha support where needed, provenance metadata, and successful prototype loading. Visual quality remains a release review rather than a pixel-perfect unit test.
- Unit tests may cover pure configuration validation, score calculations, serialization, and compatibility parsing, but do not replace public-boundary tests.
- Pull-request CI runs formatting, static checks, configuration validation, and pure unit tests without external model credentials.
- A headless-Factorio integration job runs on the default branch, on demand, nightly, and for release candidates.
- The scripted baseline must pass the full task from a clean environment; every negative or adversarial baseline must fail for its intended reason.
- Test artifacts include the seed, full version matrix including image tag and digest, action/code trajectory, evaluator output, violations, cross-check data, logs, and final replay reference.
- Prior art is FLE's code-action environment and task verification model, but v0.1 owns its container, registration, seed, custom-prototype, timing, and evaluator compatibility behavior.

## Out of Scope

- Dynamic commodity prices, procurement budgets, market orders, revenue, profit, and supply shocks
- Real-world semiconductor process fidelity, fab yield modeling, lithography details, or validated cost data
- Mars, rockets, orbital logistics, ISRU, LOX/CH4 production, and settlement loops
- Space Age as a required dependency
- Multi-agent coordination, firms, negotiation, or competitive markets
- Reinforcement-learning training infrastructure or a distributed rollout cluster
- A public leaderboard or untrusted-agent execution service before full network and RCON isolation
- Native keyboard, mouse, or vision-only control
- Unity or any standalone game engine
- Procedural generation of all new resources across arbitrary maps
- A large content pack, full campaign, or polished commercial-grade art set
- Backward compatibility with arbitrary FLE and Factorio versions

## Further Notes

This specification validates the smallest research-relevant vertical slice. The next specification should add economic operations and one deterministic copper-supply shock using the same production chain. The Mars ISRU line remains a later domain pack rather than being coupled to the first integration.

The highest-level test seam is the public classic `gym`/FLE environment contract. Compatibility-specific lower-level seams are required only where FLE 0.4.3 lacks a supported extension point or observable contract.

On 2026-07-21, the owner confirmed this public environment lifecycle as the sole primary acceptance seam, `compute-unit` as a real item, and the v0.1 cooperative-agent, audit-enforced threat model. This specification is ready for the repository-bootstrap task and required integration spike. Full prototype and art implementation remains gated on a spike `GO` result.
