# Roadmap

## Phase 0 — executable prototype
- [x] Lexer, expression parser, and basic interpreter
- [x] Immutable/mutable binding distinction
- [x] Bounded EMA telemetry and opt-in auto engine
- [x] Unit tests and sample program

## Phase 1 — language foundation
- [ ] Source spans and stable diagnostics
- [ ] Explicit static type checker
- [ ] Module system, blocks, functions, and return values

## Phase 2 — type and safety model
- [ ] Algebraic data types, generics, exhaustive matching
- [ ] Result/Option types and error propagation
- [ ] Ownership/borrowing and deterministic cleanup

## Phase 3 — runtime and concurrency
- [ ] Structured tasks and cancellation propagation
- [ ] Reproducible benchmarks, fuzzing, property tests

## Phase 4 — native compiler
- [ ] Intermediate representation and optimization pipeline
- [ ] Evaluate LLVM or another native backend
- [ ] SIMD, inlining, escape analysis, profile-guided optimization

## Phase 5 — performance validation
- [ ] Choose workloads and credible baselines
- [ ] Publish raw benchmark data and environment details
- [ ] Measure throughput, latency, memory, and tail pauses
- [ ] Treat any 16x–32x gain as unproven until replicated
