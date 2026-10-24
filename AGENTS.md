# Working in this repository

## What this project is

Axiom is an experimental language **prototype whose deliverable is a CLI**:
`python -m axiom <file.ax>` runs a small Python-hosted interpreter for an Axiom
subset (`axiom/compiler.py`), plus an opt-in bounded EMA telemetry engine
(`axiom/adaptive.py`, `axiom/auto_engine.py`). There is no web UI, no database,
no network service and **no third-party dependency** — it is Python 3.10+ stdlib
only, so nothing needs to be installed to run it. `SPEC.md`, `ROADMAP.md` and
`DESIGN_NOTES.md` describe design goals; most of the language (types, pattern
matching, concurrency, native codegen) is explicitly *planned, not implemented*.
Do not describe roadmap items as working features, and do not add performance
claims: the 16x–32x figure in the repo is a research target, unmeasured.

## Layout (keep it this way)

`pyproject.toml` declares `packages = ["axiom"]`, and the tests import
`axiom.compiler` / `axiom.adaptive`. The modules therefore have to live inside an
`axiom/` package directory with the tests in `tests/` and programs in
`examples/`. At import time all of these files sat loose at the repository root,
which made every documented command fail (`No module named axiom`,
`Start directory is not importable: 'tests'`) — moving them into `axiom/`,
`tests/` and `examples/` is what makes the repo runnable. Do not move them back
to the root.

## Commands

```bash
python -m unittest discover -s tests -v     # 13 tests, all pass
python -m axiom examples/hello.ax           # prints 42
python -m axiom --telemetry examples/hello.ax   # adds an elapsed/baseline line
```

## Sandbox preview

The Base44 preview is a browser, and this project has no web surface, so
`docker-compose.base44.yml` runs `dev/preview.py` on host port 3000. That harness
is **sandbox-only development tooling, not part of the Axiom project**: it adds
no language features and holds no application logic — it runs the project's own
documented commands as subprocesses (`python -m axiom --telemetry examples/*.ax`
and the unittest discovery above) and renders their real stdout/stderr, freshly
on every request. It never imports the interpreter, so edits to `axiom/*.py` take
effect on the next page load with no restart. Nothing else in the sandbox needs
`BASE44_PREVIEW_MODE`: no shared application configuration is overridden, so the
project behaves identically inside and outside the sandbox.

```bash
docker compose -f docker-compose.base44.yml up -d --build
curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:3000/   # expect 200
```

## Ignore

`TEST_RESULTS.txt` keeps a stale copy of an unrelated `artifact_tool` spreadsheet
traceback above the real test log; it means nothing for this project.
