# Axiom

Axiom is an experimental language project exploring safer systems programming, concise error handling, structured concurrency, and adaptive runtime policies.

**Status:** early prototype. The executable is a small Python-hosted interpreter for a limited Axiom subset. It is not a native compiler and makes no verified 16x–32x performance claim.

## Quick start

Requires Python 3.10+.

```bash
python -m axiom examples/hello.ax
python -m unittest discover -s tests -v
```

Example:

```axiom
let base = 40
let adjustment = 2
print(base + adjustment)
```

## Goals

- Explicit Result and Option types, with concise error propagation.
- Algebraic data types, generics, and exhaustive pattern matching.
- Non-null references and explicit optional values.
- Structured concurrency and visible cancellation.
- Ownership/borrowing and deterministic resource cleanup.
- Immutable bindings by default; explicit mutable bindings.
- Bounded adaptive telemetry using an exponential moving average.

See `SPEC.md`, `docs/ROADMAP.md`, and `docs/DESIGN_NOTES.md`.
