# Security Policy

## Supported versions

The project is pre-release. Security fixes are made on the current default branch and, after the first release, on versions explicitly listed as supported in release notes. Unpinned combinations of Factorio, FLE, Python, and container images are outside the supported compatibility boundary.

## Reporting a vulnerability

Report suspected vulnerabilities privately through [GitHub Security Advisories](https://github.com/tsubasakong/frontier-factory-bench/security/advisories/new). Include the affected revision, the exact compatibility matrix, reproduction steps, impact, and any relevant logs with credentials removed.

Do not open a public issue for an undisclosed vulnerability. Do not include RCON passwords, model-provider keys, access tokens, or other secrets in a report. The maintainers will acknowledge and triage reports on a best-effort basis; no fixed response-time commitment is made before the project has a staffed security process.

## Current implementation status

The repository-bootstrap task (tracked as GitHub issue #2) provides governance, locked lightweight dependencies, unit
tests, and pinned CI. It does **not** yet execute agent code or implement the
runtime evaluator controls described below. The mod-storage evaluator,
read-only remote interface, action log, three-count invariant, and adversarial
baselines are planned work in Tasks 7–11. Until those tasks are complete and
verified, do not interpret this repository as providing benchmark-integrity
controls and do not run untrusted agent code.

## v0.1 required threat model

The formal posture is the **v0.1 cooperative-agent, audit-enforced threat model**. FLE code actions execute agent-supplied Python. That Python can potentially reach local process, filesystem, network, and credential state, and FLE's privileged RCON path can execute Lua capable of changing game state or production statistics. Treat every agent code payload as untrusted arbitrary code and run the benchmark only on a disposable machine or isolated development environment appropriate to that risk.

The completed v0.1 benchmark must implement these detection and audit controls:

- every submitted action and code payload, result, error, and relevant game tick is logged;
- authoritative evaluator state is kept in the benchmark mod's private `storage`;
- evaluator data is exposed to the adapter only through a uniquely named, read-only remote interface;
- a valid holdout requires the exact integer invariant `C_stats == C_machine == C_ledger`;
- negative and adversarial baselines exercise output buffering, direct insertion, spawn attempts, production-statistic tampering, disallowed hand crafting, holdout actions, and zero action.

Once implemented and verified, these controls are intended to detect known manipulation by a cooperative, fully logged agent. They do not contain a hostile process and do not establish a security boundary between the agent, adapter, Factorio server, evaluator, Docker daemon, or host.

In particular, v0.1 does **not** claim to prevent an agent with direct or indirect access from:

- discovering or using RCON credentials;
- connecting to RCON or evaluator control ports;
- reading or changing host files, environment variables, process state, or Docker state;
- opening arbitrary network connections;
- attacking FLE, Factorio, dependencies, or the operating system;
- persisting state outside the intended reset boundary.

Do not accept untrusted public submissions or operate a public leaderboard under the v0.1 model.

## Public-leaderboard security gate

Before any public leaderboard or untrusted-agent service, the project must complete a separate security review and, at minimum:

- isolate the agent, adapter, Factorio server, and evaluator into least-privilege processes or containers;
- prevent the agent network namespace from reaching RCON and evaluator control ports;
- keep RCON credentials out of agent-readable files, environment variables, process arguments, and logs;
- expose only an allowlisted action service to the agent while keeping evaluator reads and holdout control private;
- reject background or in-flight agent work during evaluator-owned holdout barriers;
- prove with credential-discovery, spawn, direct-insert, statistic-mutation, and cross-run-persistence tests that tampering cannot produce a valid score.

See the [walking-skeleton specification](docs/specs/SPEC_001_WALKING_SKELETON.md), [acceptance plan](docs/planning/REPO_BOOTSTRAP_AND_ACCEPTANCE.md), and [compatibility matrix](docs/compatibility.md) for the normative benchmark contracts.
