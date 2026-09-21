# RegenBench

**RegenBench** is a benchmark for evaluating whether coding-agent patches remain correct after canonical regeneration of derived source artifacts.

The benchmark targets a failure mode that ordinary test-based evaluation can miss: an agent may patch generated code directly, causing tests to pass temporarily, while leaving the canonical source of truth unchanged. The patch disappears the next time the repository runs its normal code-generation pipeline.

## Core property

A task is not considered fully solved merely because tests pass immediately after the agent patch. RegenBench performs a second-stage verification:

1. Run the task tests on the agent-modified repository.
2. Run the repository's canonical regeneration command.
3. Re-run the same task tests.
4. Inspect whether the patch touched the canonical source and/or only generated artifacts.

The primary outcome is **regeneration survival**.

## Why this matters

Generated artifacts are common in production repositories:

- Protobuf / gRPC
- OpenAPI / generated SDKs
- GraphQL code generation
- ORM schemas and generated models
- ANTLR and parser generators
- Thrift / FlatBuffers / Avro
- API bindings and language clients
- Build-system and configuration code generation

A patch can therefore be functionally correct at time *t* but structurally wrong in the repository's source-of-truth model.

## Metrics

- **Pre-Regen Pass Rate (PRR):** fraction of tasks passing before regeneration.
- **Post-Regen Pass Rate (PoRR):** fraction passing after canonical regeneration.
- **Regeneration Survival Rate (RSR):** among initially passing tasks, fraction that still pass after regeneration.
- **Generated-Only Repair Rate (GORR):** fraction of successful pre-regeneration patches that modify generated artifacts but no canonical source.
- **Source-of-Truth Repair Rate (STR):** fraction of solved tasks whose patch modifies an authoritative source and survives regeneration.

## Quick start

The repository includes one fully self-contained seed task that uses a tiny JSON-schema-to-Python generator. It requires only Python 3.10+.

```bash
cd RegenBench
python -m regenbench evaluate \
  --task tasks/demo_python_codegen/task.json \
  --workspace tasks/demo_python_codegen/repo
```

The clean baseline intentionally fails the hidden-equivalent task test. To demonstrate the benchmark behavior, create disposable copies and apply either the bad or good example patch:

```bash
python examples/run_demo.py
```

Expected behavior:

- **Bad patch:** passes before regeneration, fails after regeneration.
- **Good patch:** passes before regeneration and still passes after regeneration.

## Task format

Each task is described by JSON:

```json
{
  "id": "demo_python_codegen_001",
  "test_command": ["python", "-m", "unittest", "discover", "-s", "tests"],
  "regenerate_command": ["python", "tools/generate.py"],
  "canonical_sources": ["schema/**", "tools/generate.py"],
  "generated_artifacts": ["generated/**"]
}
```

For real benchmark tasks, the evaluator is intended to run in an isolated worktree/container at the pre-fix commit after a coding agent has attempted the task.

## v0.1 scope

The first research milestone is not scale. It is to establish that the hidden failure gap exists on real repositories:

- 20–30 tasks
- 4–5 generation ecosystems
- 3+ coding agents
- deterministic regeneration and test commands
- real repository history where possible

Only if the regeneration gap is material should the benchmark scale toward 100–300 tasks.

## Candidate real-world ecosystems

Initial targets include repositories with explicit source/generated boundaries and reproducible generation commands, such as Protobuf, GraphQL Codegen, OpenAPI SDK generation, and parser/code-generation pipelines.

## Research question

> Can coding agents repair generated-code systems at the canonical source of truth, such that their fixes survive regeneration?
