# Review findings and confirmed decisions

Review date: 2026-07-21

This document consolidates four independent reviews of the v0.1 walking
skeleton: an FLE v0.4.3 source audit, a Factorio 2.0 modding review, a
benchmark-adversarial review, and an engineering/open-source delivery review.

## Overall conclusion

The independent-extension architecture is viable without forking FLE, but the
compatibility adapter is a first-class subsystem rather than a thin registration
shim. Full content and art work must wait for one end-to-end integration spike.

The revised spec, bootstrap plan, compatibility seam, and owner decisions were
accepted on 2026-07-21. The work breakdown is ready to begin with repository
bootstrap and the spike described below; the rest of v0.1 remains blocked by
the spike's go/no-go result.

## Confirmed project decisions

- Repository identity: [`tsubasakong/frontier-factory-bench`](https://github.com/tsubasakong/frontier-factory-bench),
  created as a public repository on 2026-07-21.
- `compute-unit` is a real Factorio item. Inventory or item movement does not
  satisfy the task; success uses production during the holdout window.
- v0.1 uses a cooperative-agent, audit-enforced threat model: complete
  action/code logs, evaluator state in mod-owned `storage`, a read-only remote
  interface, three-source measurement invariants, and adversarial baselines.
- Network/RCON isolation is required before a public leaderboard, but it is not
  a v0.1 release gate.
- The project remains an independent repository. A fork is considered only if
  the spike demonstrates that the documented adapter boundary cannot work.
- The first compatibility tuple is FLE `v0.4.3` at commit `6439e18` and
  Factorio `2.0.73` through a `factoriotools/factorio:2.0.73` image pinned by
  both tag and digest.
- Project-original visual assets use CC BY 4.0. Derived Factorio assets, if any,
  are explicitly excluded from that license and governed by applicable Wube
  terms; the v0.1 policy is to use original assets only.

## Source-confirmed compatibility boundary

1. **Mod and scenario mounting.** FLE v0.4.3 has an unconnected
   `attach_mod`/`FLE_MODS_PATH` path. The project will manage its own Factorio
   container and mount its own `mods` and scenario directories, then connect
   FLE through `FACTORIO_SERVER_ADDRESS` and `FACTORIO_SERVER_PORT`.
2. **Custom prototypes.** FLE's Python `Prototype`, `RecipeName`, and related
   enums are hard-coded. Default entity tools reject or omit custom entities.
   The adapter must provide string-based tools, preferably through a project
   `FLE_TOOLS_DIR`. Runtime mutation of enum internals is forbidden in the
   acceptance path; failure of the string-tool path is a spike `NO-GO`.
3. **Environment registration.** The project will own a classic-Gym entry point
   that directly constructs `FactorioGymEnv(instance, task)`, bypassing FLE's
   closed task registry and factory.
4. **Reset and determinism.** FLE v0.4.3 ignores `reset(seed=...)`. The adapter
   and scenario own seed semantics. RCON timing prevents a general promise of
   tick-identical world replays; the contract instead covers equal task outcome
   and a documented metric subset within declared tolerances.
5. **Holdout.** The evaluator owns the holdout, advances it without agent
   actions, and measures it using `game.tick`. Calls attempted during the
   holdout are rejected and recorded as violations.

## Measurement contract

For holdout ticks `[t1, t2]`, let `C_stats` be the integer delta of
`force.get_item_production_statistics(surface).get_input_count("compute-unit")`;
let `C_machine` be the sum of each tracked data-center node's
`delta(products_finished) * recipe_output_quantity`; and let `C_ledger` be the
mod-control completion ledger accumulated from valid data-center nodes running
the fixed recipe. A valid run requires the exact integer invariant
`C_stats == C_machine == C_ledger`. Throughput is
`C_stats * 3600 / (t2 - t1)` units per minute because Factorio runs at 60 ticks
per second.

Output inventory and scripted insertion do not satisfy the primary measure.
Legal upstream input buffers are allowed: v0.1's hard pass condition is
sustained, genuine compute production, not simultaneous production at every
upstream stage. Per-stage throughput, input consumption, power/energy state,
and theoretical-rate bounds are diagnostic and plausibility checks retained in
the run artifact.

Diagnostics include per-stage throughput, power/energy state, action error
categories, entity/resource use, elapsed ticks, uptime, and an explicit,
extensible automation-violation enum.

## Threat model boundary

FLE code actions execute agent-supplied Python and ultimately privileged Lua
through RCON. v0.1 therefore does not claim prevention against a hostile agent
with unrestricted host or RCON access. It does require auditability and
detection within the cooperative-agent, audit-enforced evaluation contract. Injection/statistics
tampering, final-stage hand crafting, actions during holdout, zero-action,
under-capacity, and output-buffer attempts are mandatory negative tests.

## Required first spike

Build the smallest vertical slice before full prototypes or art:

1. One custom item, one custom machine/recipe, and a minimal scenario.
2. An adapter-managed Factorio container with the project mod mounted.
3. FLE connected via address/port environment variables.
4. String-based placement and observation of the custom machine.
5. Real production satisfies `C_stats == C_machine == C_ledger` and the quota.
6. Output-buffer movement and scripted insertion cannot satisfy the quota;
   direct production-stat mutation creates a cross-check mismatch and an
   invalid run.
7. Agent calls during the evaluator-owned holdout are rejected and recorded.

The spike produces ADR-001 and a go/no-go decision. A no-go result triggers a
fork/upstream-hook reassessment; a go result unlocks the remaining v0.1 child
issues.

## Remaining calibration decisions

The architecture is no longer blocked by owner choices. Recipe quantities,
starting inventory, quota, holdout length, legal intermediate-buffer limits,
and exact metric tolerances must be calibrated during the spike and passing
baseline work. They are task configuration, not unresolved architecture.
