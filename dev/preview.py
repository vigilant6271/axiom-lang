"""Sandbox-only preview harness for the Axiom prototype.

Axiom is a command-line interpreter: the deliverable is `python -m axiom <file.ax>`,
so a browser preview has nothing to render on its own. This tiny stdlib HTTP
server exists only so the Base44 preview can show the project actually working.

It is NOT part of the Axiom project and adds no language features: it simply runs
the project's own documented commands as subprocesses (`python -m axiom --telemetry
examples/*.ax` and `python -m unittest discover -s tests`) and prints their real
output, re-running them on every request so source edits show up immediately.

Usage: python dev/preview.py   (listens on 0.0.0.0:${PORT:-3000})
"""
from __future__ import annotations

import html
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("PORT", "3000"))
TIMEOUT = 30


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run one of the project's documented commands from the repo root."""
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )


def collect_reports() -> tuple[list[dict], dict]:
    examples = []
    for path in sorted((ROOT / "examples").glob("*.ax")):
        result = run_cli("-m", "axiom", "--telemetry", str(path.relative_to(ROOT)))
        examples.append(
            {
                "name": path.name,
                "source": path.read_text(encoding="utf-8"),
                "output": result.stdout.rstrip("\n"),
                "error": result.stderr.rstrip("\n"),
                "returncode": result.returncode,
            }
        )

    tests = run_cli("-m", "unittest", "discover", "-s", "tests", "-v")
    return examples, {
        "ok": tests.returncode == 0,
        "output": (tests.stdout + tests.stderr).rstrip("\n"),
    }


def render_page(examples: list[dict], tests: dict) -> str:
    def block(text: str, css_class: str = "code") -> str:
        return f'<pre class="{css_class}">{html.escape(text) or "&nbsp;"}</pre>'

    sections = []
    for example in examples:
        status = "ok" if example["returncode"] == 0 else f"exit {example['returncode']}"
        parts = [
            f'<h2>{html.escape(example["name"])} <span class="badge {"" if example["returncode"] == 0 else "bad"}">'
            f"{status}</span></h2>",
            "<h3>Source</h3>",
            block(example["source"]),
            "<h3>Output</h3>",
            block(example["output"]),
        ]
        if example["error"]:
            parts += ["<h3>Diagnostics</h3>", block(example["error"], "code bad-text")]
        sections.append("\n".join(parts))

    tests_summary = "all tests pass" if tests["ok"] else "test failures"
    sections.append(
        f'<h2>Test suite <span class="badge {"" if tests["ok"] else "bad"}">'
        f"{html.escape(tests_summary)}</span></h2>"
        f'<p class="hint">python -m unittest discover -s tests -v</p>'
        f"{block(tests['output'])}"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Axiom prototype — sandbox preview</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin: 0; padding: 2.5rem 1.25rem; background: #14161a; color: #e7e9ee;
         font: 15px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 60rem; margin: 0 auto; }}
  h1 {{ font-size: 1.5rem; margin: 0 0 .35rem; }}
  h2 {{ font-size: 1.05rem; margin: 2rem 0 .5rem; border-bottom: 1px solid #2a2e36; padding-bottom: .4rem; }}
  h3 {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; color: #98a1b3;
        margin: 1.1rem 0 .35rem; }}
  .hint {{ color: #98a1b3; margin: .25rem 0 .5rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
           font-size: .82rem; }}
  .code {{ background: #1c1f25; border: 1px solid #2a2e36; border-radius: 8px; padding: .75rem .9rem;
           margin: 0; overflow-x: auto; white-space: pre-wrap; word-break: break-word;
           font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .85rem; }}
  .bad-text {{ color: #ffb4a8; }}
  .badge {{ font-size: .7rem; font-weight: 600; vertical-align: middle; padding: .15rem .45rem;
            border-radius: 999px; background: #1f3d2b; color: #86e2a8; text-transform: none;
            letter-spacing: 0; }}
  .badge.bad {{ background: #3d2121; color: #ffb4a8; }}
  .note {{ background: #1c1f25; border: 1px solid #2a2e36; border-left: 3px solid #6f7dff;
           border-radius: 8px; padding: .8rem .9rem; color: #b9c1d1; }}
</style>
</head>
<body>
<main>
  <h1>Axiom prototype — running in the sandbox</h1>
  <p class="note">Axiom is a command-line interpreter, so this page is a development
  harness rather than app UI: it runs the project's own CLI and test suite below,
  freshly on every request. The interpreter is a Python-hosted prototype for a small
  Axiom subset — no native compiler, and nothing here is a performance claim.</p>
  {''.join(sections)}
</main>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "AxiomPreview/1.0"

    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?")[0] not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return
        try:
            examples, tests = collect_reports()
            body = render_page(examples, tests).encode("utf-8")
        except (subprocess.SubprocessError, OSError) as exc:
            body = f"preview harness error: {html.escape(str(exc))}".encode("utf-8")
            self.send_response(500)
        else:
            self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("preview %s\n" % (fmt % args))


def main() -> int:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"axiom preview harness on http://0.0.0.0:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
