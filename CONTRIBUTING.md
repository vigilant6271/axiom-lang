# Contributing

Axiom is experimental. The specification is a proposal and the executable subset is intentionally small.

## Development

Requires Python 3.10+.

```bash
python -m unittest discover -s tests -v
python -m axiom examples/hello.ax
```

## Guidelines

- Keep behavior explicit and diagnostics actionable.
- Add tests for every syntax or runtime behavior change.
- Do not describe planned features as implemented.
- Adaptive behavior must be bounded, testable, and opt-in by default.
- Performance claims require reproducible measurements and methodology.
- Discuss major grammar or memory-model changes before implementation.

When reporting a bug, include a minimal source example, expected behavior, actual behavior, Python version, and error text.
