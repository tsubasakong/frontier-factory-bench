# Glossary

## Architecture terms

**Module**
: Anything with an interface and an implementation, deliberately independent of scale. Examples include the Factorio mod, Python adapter, evaluator, task definitions, and baseline scripts. A module must not make another module depend on its private implementation. In this repository, “module” is the architecture term; the Factorio content package is specifically called the “mod.”

**Interface**
: Everything a caller must know to use a module correctly: accepted inputs, observable outputs, invariants, ordering constraints, errors, lifecycle, and version assumptions. The primary public interface is the project's self-registered classic-Gym/FLE environment lifecycle: create, reset, act, observe, verify, terminate, close, and export artifacts.

**Seam**
: The location where a module's interface lives and where behavior can be altered without editing the caller. The public environment lifecycle is the primary acceptance seam; lower-level compatibility seams exist only where pinned FLE behavior lacks a sufficient public extension point.

**Adapter**
: The project-owned Python compatibility layer between FLE `v0.4.3`, the self-managed Factorio server, and Frontier Factory task code. It owns environment registration, container connection, seeded reset behavior, string-based custom-prototype tools, error translation, and cleanup. It does not create a second agent-facing action protocol.

## Benchmark terms

**`compute-unit`**
: The real, storable Factorio item produced by the fixed recipe in tracked data-center nodes. Inventory quantity or movement of prebuilt items never counts as task success; only valid recipe completions during the holdout count.

**Holdout**
: The evaluator-owned verification interval beginning at tick `t1` and ending at tick `t2`, with duration `t2 - t1`. Before it begins, the evaluator establishes a barrier and freezes the tracked data-center-node set. During it, agent API calls are rejected before execution and logged as violations. Throughput is `C_stats * 3600 / (t2 - t1)` compute units per minute.

**`C_stats`**
: The integer holdout delta of `force.get_item_production_statistics(surface).get_input_count("compute-unit")` on the configured surface.

**`C_machine`**
: The integer sum across tracked data-center nodes of each machine's holdout `products_finished` delta multiplied by the compute-unit recipe output quantity.

**`C_ledger`**
: The integer completion count maintained in the benchmark mod's private `storage`. It records verified fixed-recipe completions from tracked data-center nodes and adds the recipe output quantity for each completion.

**Three-count invariant**
: The exact requirement `C_stats == C_machine == C_ledger`. Any mismatch invalidates the run; meeting the invariant alone does not pass unless the configured throughput quota is also met.

**`GO`**
: The Task 2 integration-spike result emitted only when every machine-checkable checklist item passes under the exact pinned compatibility matrix. `GO` unblocks complete prototype and production-art work.

**`NO-GO`**
: The integration-spike result when any required checklist item fails. `NO-GO` blocks dependent implementation and reopens the relevant architecture decision. Failure of string-based custom-prototype tools is `NO-GO`; runtime mutation of FLE's prototype enums is not an acceptance fallback.

**v0.1 cooperative-agent, audit-enforced threat model**
: The v0.1 security posture in which arbitrary agent Python and privileged RCON effects are disclosed and known manipulation is detected through complete logs, mod-owned evaluator state, a read-only remote interface, the three-count invariant, and adversarial baselines. It is not hostile-process isolation and is insufficient for a public leaderboard.
