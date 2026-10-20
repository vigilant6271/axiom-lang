"""CLI entry point: python -m axiom [--telemetry] file.ax."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from .compiler import AxiomError
from .auto_engine import AutoEngine


def main() -> int:
    parser = argparse.ArgumentParser(prog="axiom", description="Run an Axiom prototype source file.")
    parser.add_argument("file", type=Path, help="Axiom source file (.ax)")
    parser.add_argument("--telemetry", action="store_true", help="enable bounded timing telemetry")
    args = parser.parse_args()
    try:
        source = args.file.read_text(encoding="utf-8")
        report = AutoEngine(telemetry=args.telemetry).execute(source)
        if report.adaptation:
            print(f"[axiom telemetry] elapsed={report.elapsed_seconds:.6f}s baseline={report.adaptation.baseline:.6f}s")
        return 0
    except (OSError, AxiomError) as exc:
        print(f"axiom: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
