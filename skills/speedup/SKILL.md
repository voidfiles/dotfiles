---
name: speedup
description: "Diagnose and improve slow tests, builds, scripts, requests, or data pipelines using profiling and comparable measurements. Use for requests to speed up a workload, investigate performance regressions, or turn a profile into a verified optimization."
---

# Speedup

Find the work that limits the user's actual wait, remove its cause, and verify the result without weakening behavior. A profile is evidence for an investigation; a smaller counter is evidence of less work. Neither alone proves an end-to-end speedup.

## Establish a runnable baseline

- Identify the workload, representative inputs, success conditions, and metric the user cares about. Distinguish full-suite time, developer feedback time, request latency, throughput, and resource consumption. Improve the requested one.
- Read the existing runner, relevant CI configuration, and available profiling commands. Reuse them before adding tools. Follow the repository's worktree, dependency, and publication rules; this skill grants no additional permissions.
- Verify the selected checkout, runtime, database, assets, and environment. Use the actual entry point the user runs. If setup fails, reproduce the first failure with a focused run before launching another expensive capture. Separate environment repair from performance changes.
- Record the revision and local changes, command, inputs or test IDs, runtime/tool versions, relevant configuration, cache/database state, and concurrent load with the baseline. Keep raw artifacts in a distinct run directory so reruns preserve earlier evidence.

For a long investigation, keep a compact evidence log in the existing artifact directory: hypothesis, command/artifact, observation, next decision. Update it when a result changes the direction, not for every tool call.

## Attribute the cost before choosing a fix

Use the least instrumentation that answers the current question. Profile a representative run, map the costly stacks to source, then collect more specific evidence where needed. Keep heavily traced diagnostic runs separate from timing comparisons.

- **Interpret the clock.** Distinguish elapsed time, CPU time, inclusive time, self time, and sampled thread time. A wait frame can include server execution, locks, communication, or idle time. Check profiler flags and coverage before interpreting percentages. Do not add overlapping inclusive times or treat one thread's samples as total process time.
- **Separate phases.** Attribute startup/collection, initialization, setup, useful work, teardown, and viewer/report launch where applicable. A first test that creates a database is not a representative fixture measurement.
- **Measure frequency and accumulated cost.** Group repeated operations and retain count, total duration, and slow outliers. Thousands of cheap operations and three expensive operations may require different fixes. Rank by contribution to the target metric, not count alone.
- **Check instrumentation boundaries.** Establish what threads, subprocesses, connections, fetches, and external work the recorder includes. Client-side database execution duration is not a server-only execution measurement. Missing events are not proof that no work happened.
- **Treat failed reproduction as evidence.** If an isolated case is fast but the suite is slow, investigate order, accumulated data, cache state, concurrency, and instrumentation differences. Do not silently replace the original workload with the easy reproduction.

Write a falsifiable hypothesis before editing: "Repeated prerequisite publication accounts for most setup queries; building the saved prerequisite once should reduce setup work while preserving public readback." Name the observation that would disprove it. When server-side SQL dominates, inspect the query plan and server activity before choosing an index, rewrite, or connection change. Use a safe test environment for tools that execute statements, including EXPLAIN ANALYZE.

## Remove the cause while preserving the contract

Choose a bounded change at the source of the repeated or expensive work. Estimate the maximum possible end-to-end benefit from the measured share before starting a large refactor. Keep independent bottlenecks as separate experiments so their effects remain attributable.

- Eliminate unnecessary work before adding concurrency. If concurrency is the hypothesis, measure contention and the limiting resource rather than assuming more workers help.
- Bound caches and reused state to a lifetime that preserves correctness. Authorization reuse must preserve revocation and expiration semantics. Confirm invalidation and ownership before broadening cache scope.
- Preserve outputs, errors, permissions, isolation, durability, and required coverage. Skipping assertions, shrinking a scale dataset, sharing mutable fixtures, or accepting stale data changes the contract and needs explicit scope agreement.
- Add focused behavioral regression checks and stable work budgets where they protect the improvement. A query budget should allow harmless implementation variation and exclude unrelated initialization. Use end-to-end timing to assess actual user benefit.
- Change one hypothesis at a time, verify it, and re-profile if the limiter moves. When results contradict the hypothesis, revisit the explanation before stacking another patch. Remove only your own unsuccessful experiment, preserving unrelated concurrent edits.

### When speeding up tests

Request the smallest prerequisite each test needs. Split broad fixtures into explicit layers and migrate consumers, including browser tests, before removing the broad fixture. Preserve fresh mutable records and credentials per test; cache immutable source data only when appropriate.

Distinguish preparing saved state from testing its creation. A cheaper valid builder can prepare data for read/compute tests; authoring, retry, transaction, and concurrency tests must still exercise the real behavior they claim to verify. Validate replacement builders through public reads, permissions, and mutation-isolation checks. Issue snapshot credentials after the grants they must contain exist.

Keep realistic full-size fixtures for completeness, pagination, scale, and query-growth tests. Make prerequisites explicit when fixture changes expose hidden dependencies; preserve the original assertions. For browser races, inspect the trace and wait for the intended visible state or completed operation before the next action. Preserve persistence checks; avoid arbitrary sleeps and weaker assertions as speed fixes.

## Verify correctness and measure the improvement

Run the checks relevant to the changed behavior using the project's normal runner. Exercise affected browser or integration paths when their prerequisites or lifecycle changed. Broaden validation when failures or the dependency graph justify it.

For an improvement claim:

1. Compare the same successful workload on both revisions with equivalent configuration, data, cache policy, and concurrency. Confirm expected work and outputs, plus failure/skip/retry counts. Exclude failed, interrupted, or incomplete runs from successful-workload timing comparisons; retain them as diagnostic evidence.
2. Measure without diagnostic tracing unless instrumentation itself is the target. Separate setup savings from steady-state savings and report cold/warm behavior separately when relevant.
3. Repeat and interleave baseline/candidate runs to limit warmup and load drift. Use enough runs to characterize spread; five per side is a useful starting point for inexpensive runs, not a reason to launch ten costly full suites automatically. Label a single-run estimate explicitly. If the apparent gain is within observed variation, report no measurable difference or inconclusive evidence.
4. Report elapsed time with units, run count, median and range, and the measured limiting component. Check that claimed savings fit within the component's original share. Report operation-count reductions separately from latency or throughput changes.

If equivalent baseline execution is unavailable, report the verified structural change and the measurement gap. Do not manufacture a speedup from unmatched artifacts. Stop when the requested improvement is verified, remaining differences are below measurement resolution, or the next experiment requires broader scope. Preserve useful evidence and state the remaining uncertainty.

## Verify the handoff path

When changing a profiler or runner, test its real launch path, output artifact, exit status, and viewer separately. Privilege changes can alter HOME, login identity, PATH, database defaults, and file ownership even if the child process drops privileges. Synthetic command checks do not establish that the elevated command works on the user's machine. If interactive verification is unavailable, name that exact gap.

State where the change is available: local checkout, task branch, open PR, or merged default branch. Verify that the supplied command uses that version. Never imply that an unmerged fix is already available from the user's default checkout.

## Deliver the result

Lead with the verified outcome: faster, less work with runtime unproven, no measurable difference, or inconclusive. Include the cause and fix, one primary before/after metric with its measurement conditions, correctness checks, and links to code and raw evidence. Name remaining bottlenecks separately from completed fixes. Keep the report short enough that the user can assess the claim without replaying the investigation.
