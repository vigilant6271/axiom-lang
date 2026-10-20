# Axiom Language Specification (Draft 0.1)

This is a design target, not a claim that every feature is implemented. The current interpreter supports only a small executable subset.

## Syntax example

```axiom
let answer = 40 + 2
var attempts = 0
attempts = attempts + 1
print(answer)
```

Statements end at a newline or semicolon. Comments begin with `#`.

## Bindings and values

- `let name = expr` declares an immutable binding.
- `var name = expr` declares a mutable binding.
- Assignment to `let` is currently rejected at runtime; a future static checker will reject it at compile time.
- Prototype values: integers, floats, strings, booleans.
- Static typing and inference are design goals; the prototype currently evaluates dynamically.

## Errors and types (planned)

The target API uses `Result<T, E>` for recoverable failures and `Option<T>` for absent values. The `?` operator propagates compatible errors. Algebraic data types, generic functions, and exhaustive `match` expressions are planned, not implemented yet. Nullable references will not be the default.

## Memory and concurrency (planned)

The systems target is ownership and borrowing with compile-time aliasing/lifetime checks and deterministic cleanup. Structured tasks should be lexically scoped, inherit cancellation, and make detached work conspicuous. These features are not implemented yet.

## Adaptive engine

The experimental engine computes an EMA baseline:

`baseline_t = alpha * sample_t + (1 - alpha) * baseline_(t-1)`

where `0 < alpha <= 1`. Telemetry is bounded and opt-in. The engine reports observations but does not silently change program semantics.

## Performance goals

The aspirational 16x–32x speedup is a hypothesis, not a guarantee. Each benchmark must state baseline, hardware, flags, workload, warm-up, and statistical method. Native code generation and optimization are future work.
