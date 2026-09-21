# Initial Real-Repository Candidate Pool

This is a **screening list**, not yet a finalized benchmark set. The v0.1 goal is to favor repositories whose generation pipeline can be reproduced cheaply in an isolated environment.

## Tier A — promising for early tasks

### OpenIAP GraphQL schema/codegen

Repository: `hyodotdev/openiap-gql`

Why it is attractive:

- clearly declares the GraphQL schema under `src/` as the single source of truth;
- generated TypeScript output lives at `src/generated/types.ts`;
- generation is exposed as `npm run generate`;
- the source/generated relationship is easy to explain and verify.

Potential task family: schema changes that should propagate into generated TypeScript types.

### go-e2b

Repository: `matiasinsaurralde/go-e2b`

Why it is attractive:

- explicit vendored Protobuf source under `proto/`;
- generated Go code under `internal/gen/` is marked DO NOT EDIT;
- documented `make proto-sync` workflow;
- Go tests are conventional and likely automatable.

Potential task family: protocol/schema changes that must survive proto regeneration.

### Hailo Node bindings

Repository: `jordanskole/hailo-node`

Why it is attractive:

- Protobuf schema under `proto/`;
- generated JS and TypeScript declaration files under `src/generated/`;
- generation script is explicit (`scripts/generate-proto.ts`).

Risk: runtime tests may require Hailo hardware, so only generator-local tasks should be considered.

## Tier B — strong realism but heavier setup

### Vitess

Repository: `vitessio/vitess`

Why it is attractive:

- extensive real production code generation;
- explicit rule that `go/vt/proto/` is generated from `proto/*.proto`;
- documented `make proto` and `make codegen` commands;
- also contains generated SQL parser artifacts.

Risk: very large repository and expensive environment. Better for later benchmark scaling than for the first seed tasks.

### NVIDIA nv-config-manager

Repository: `NVIDIA/nv-config-manager`

Why it is attractive:

- generated OpenAPI specs and Go clients;
- explicit `make api-generate` command;
- contributor instructions explicitly require source/schema or generator-template fixes rather than direct generated-code edits.

Risk: project setup may be heavier than a compact v0.1 task needs.

### worldmonitor

Repository: `koala73/worldmonitor`

Why it is attractive:

- committed generated artifacts;
- documented `make generate` workflow;
- CI already reasons about codegen drift.

Risk: generation depends on pinned external tools and may need more container setup.

## Candidate selection procedure

For each repository, find historical commits/PRs satisfying most of the following:

1. a canonical source or generator input changed;
2. generated output changed in the same patch;
3. tests or behavior demonstrate why the change was needed;
4. the pre-fix revision can be built in isolation;
5. regeneration is deterministic or can be normalized;
6. a plausible generated-only patch could make pre-regeneration tests pass.

A repository enters v0.1 only after one full task can be reconstructed end-to-end.
