# RegenBench v0.1 Benchmark Specification

## 1. Evaluation target

RegenBench evaluates **source-of-truth correctness under canonical regeneration**.

A coding-agent patch is regeneration-stable when all of the following hold:

1. The agent-modified worktree passes the task-specific tests.
2. The repository's canonical code-generation pipeline completes successfully.
3. The regenerated worktree still passes the task-specific tests.

For tasks explicitly requiring changes to generated-code systems, the evaluator also records whether canonical source files and generated artifacts were modified.

## 2. Why ordinary test success is insufficient

Checked-in generated artifacts can make an incorrect maintenance strategy appear correct. Directly editing generated output can satisfy present tests while violating the repository's durable source model. The error is exposed only after regeneration.

RegenBench therefore treats regeneration as part of the semantic lifecycle of the repository rather than a cosmetic build step.

## 3. Task requirements

A v0.1 task should provide:

- a fixed base commit or immutable repository snapshot;
- a natural-language issue/task;
- one deterministic test command;
- one deterministic canonical regeneration command;
- patterns identifying canonical sources;
- patterns identifying generated artifacts;
- an isolated execution environment or reproducible dependency lock;
- hidden tests where public tests would leak the target patch.

## 4. Task inclusion criteria

Prefer tasks where:

- generated artifacts are checked into the repository or materially consumed by tests/builds;
- the source/generated relationship is explicit and reproducible;
- regeneration is deterministic enough for automated grading;
- the human fix modifies canonical sources or generator logic;
- a plausible direct-generated-file patch could satisfy pre-regeneration tests.

Exclude tasks where:

- regeneration requires inaccessible proprietary infrastructure;
- generated artifacts contain timestamps/non-determinism that cannot be normalized;
- the issue is unrelated to generated artifacts and regeneration cannot distinguish repair strategies;
- environment setup dominates the task.

## 5. Primary metrics

Let `pre_i` indicate task i passes before regeneration and `post_i` indicate it passes after successful canonical regeneration.

### Pre-Regen Pass Rate (PRR)

`sum(pre_i) / N`

### Post-Regen Pass Rate (PoRR)

`sum(post_i) / N`

### Regeneration Survival Rate (RSR)

`sum(pre_i and post_i) / sum(pre_i)`

This is the core metric: among patches that look correct initially, how many remain correct after the repository rebuilds its generated artifacts?

### Generated-Only Repair Rate (GORR)

Among pre-regeneration successes, fraction that touch generated artifacts but no canonical source.

### Source-of-Truth Repair Rate (STR)

Fraction of tasks that survive regeneration and modify the authoritative source layer expected for the task.

## 6. Failure taxonomy

- **Direct Artifact Patch** — generated output changed, source of truth unchanged.
- **Partial Source Repair** — source touched but regeneration still loses required behavior.
- **Generator Bypass** — agent alters build/generation workflow to avoid canonical regeneration rather than solving the source issue.
- **Stale Checked-in Artifact** — source is correct but required checked-in generated outputs are not synchronized.
- **Regeneration-Safe Repair** — canonical source is fixed and task correctness survives regeneration.

## 7. Two evaluation settings

### Explicit provenance

Repository instructions identify generated artifacts and canonical source locations. Measures instruction-following plus repair correctness.

### Implicit provenance

Those instructions are removed while the repository itself remains intact. Measures whether the agent can infer source/generated provenance from build scripts, headers, directory structure, and generator configuration.

## 8. v0.1 target composition

Target 20–30 real tasks across at least four ecosystems, e.g.:

- Protobuf/gRPC
- OpenAPI/SDK generation
- GraphQL Codegen
- parser/schema/ORM generation

A task family should not dominate the benchmark. Results should be reported both overall and per ecosystem.

## 9. Go/no-go criterion for scaling

Before scaling past v0.1, run at least three strong coding agents. If the difference between PRR and PoRR is negligible across agents, the failure mode is not empirically important enough for a large benchmark. A material hidden failure gap (for example, repeated double-digit regeneration failures among otherwise passing patches) justifies expansion.
