# Frontier Factory Bench

> Working title: an open research environment for evaluating industrial agents in a modded Factorio world.

[![CI](https://github.com/tsubasakong/frontier-factory-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/tsubasakong/frontier-factory-bench/actions/workflows/ci.yml)

## Status

Pre-M0. The repository bootstrap is implemented and verified; the required
integration spike is next. Complete prototype and art work is blocked until
that spike records a `GO` decision in ADR-001. The four-way review and confirmed decisions are in
[docs/reviews/REVIEW_FINDINGS.md](docs/reviews/REVIEW_FINDINGS.md).

- GitHub parent spec: [issue #1](https://github.com/tsubasakong/frontier-factory-bench/issues/1)
- Bootstrap implementation: [issue #2](https://github.com/tsubasakong/frontier-factory-bench/issues/2)
- Spec: [docs/specs/SPEC_001_WALKING_SKELETON.md](docs/specs/SPEC_001_WALKING_SKELETON.md)
- Bootstrap and acceptance plan: [docs/planning/REPO_BOOTSTRAP_AND_ACCEPTANCE.md](docs/planning/REPO_BOOTSTRAP_AND_ACCEPTANCE.md)
- Supporting source and modding review reports: [docs/reviews/2026-07-21/](docs/reviews/2026-07-21/)

## Bootstrap

Prerequisites for lightweight development are Python 3.12.9, `uv` 0.9.10,
and GNU Make. Docker is not required for bootstrap, linting, unit tests, or
packaging.

```bash
make bootstrap
make test
make package
```

`make smoke`, `make demo`, and `make benchmark` are reserved for Task 2 and
later. They require Docker and currently fail explicitly instead of reporting a
false success. The exact supported dependency tuple is recorded in
[docs/compatibility.md](docs/compatibility.md).

## One-line thesis

Frontier Factory Bench evaluates whether an AI agent can plan, build, operate, and recover an industrial production system under physical, capacity, energy, and economic constraints—not merely complete isolated crafting tasks.

## Why this project

Existing Factorio agent environments already test long-horizon planning, code-driven interaction, spatial reasoning, and production automation. This project adds a deliberately out-of-distribution industrial domain with original materials, machines, graphics, technology trees, and later market dynamics.

The research progression is:

1. **AI infrastructure:** quartz/silicon → wafer → AI accelerator → server rack → data center → compute output.
2. **Industrial economics:** budgets, procurement, inventory, capacity constraints, energy costs, demand, and deterministic shocks.
3. **Space industrialization:** launch systems and Mars in-situ resource utilization, including water/CO2 processing and LOX/CH4 production.
4. **Embodied industrial agents:** multi-agent operations, robotics-style workcells, fault recovery, maintenance, and scheduling.

## Intended users

- Frontier-model and agent-evaluation researchers
- Reinforcement-learning and LLM-agent engineers
- Industrial AI, manufacturing, and supply-chain researchers
- Factorio modders and benchmark contributors
- Educators demonstrating production systems and technology dependencies

## Project boundaries

This is a stylized benchmark, not a validated digital twin of semiconductor fabrication, data-center finance, launch operations, or Mars settlement. The first releases optimize for controllability, reproducibility, and research signal rather than exact industrial fidelity.

## Recommended architecture

Use one public monorepo with six logical modules:

1. **Factorio domain mod** — prototypes, recipes, technologies, runtime rules, and original sprites.
2. **FLE compatibility adapter** — installs/enables the mod, registers environments, and enriches observations and tools.
3. **Task pack** — declarative benchmark tasks, seeds, starting states, quotas, and event schedules.
4. **Evaluator** — sustained-throughput checks, automation checks, economic metrics, score decomposition, and anti-reward-hacking rules.
5. **Baselines and replay** — reproducible scripted policies, trajectory capture, documented metric-subset comparisons, and reports.
6. **Benchmark documentation** — glossary, ADRs, benchmark card, asset provenance, and contribution guides.

## Integration policy

- Start as an **independent extension repository**, not a fork of FLE.
- Pin FLE v0.4.3 at commit `6439e18`, Factorio 2.0.73, and the tested container digest; isolate FLE-specific calls behind a compatibility adapter.
- Fork or upstream changes only after a concrete missing extension point is demonstrated.
- Depend on base Factorio 2.0 for the first release; do not require Space Age.
- Do not redistribute Factorio binaries or proprietary game assets.
- Use original project art for all new visible materials and machines.

## Release roadmap

### v0.1 — AI infrastructure walking skeleton

A visually distinct production chain and one reproducible classic-Gym task that can be completed by a scripted baseline.

### v0.2 — Economic operations

Budget ledger, spot prices, purchase capacity, energy costs, compute revenue, and one deterministic copper supply shock.

### v0.3 — Benchmark release

Multiple task difficulties, seeded evaluation suites, baseline results, replay artifacts, benchmark card, and reproducible release bundle.

### v0.4 — Mars ISRU pack

Water extraction, electrolysis, CO2 capture, Sabatier methane production, oxygen liquefaction, launch logistics, and a fuel-self-sufficiency objective.

## Success definition

The project succeeds when a third party can clone the repository, start the environment, run a reproducible scripted baseline, reproduce the published metrics within documented tolerances, and then substitute a different agent without modifying the benchmark implementation.
