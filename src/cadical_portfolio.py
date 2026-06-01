from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Variant:
    label: str
    options: tuple[str, ...]


VARIANTS: tuple[Variant, ...] = (
    Variant("baseline", ()),
    Variant("preprocess1", ("-P1",)),
    Variant("preprocess2", ("-P2",)),
    Variant("optimize1", ("-O1",)),
    Variant("optimize2", ("-O2",)),
    Variant("local1", ("-L1",)),
    Variant("local10", ("-L10",)),
    Variant("preprocess1_optimize1", ("-P1", "-O1")),
    Variant("preprocess2_optimize1", ("-P2", "-O1")),
    Variant("preprocess1_local1", ("-P1", "-L1")),
)


def select_variants(max_jobs: int, skip_baseline: bool = False, start_index: int = 0) -> list[Variant]:
    if max_jobs <= 0:
        raise ValueError("max_jobs must be positive")
    if start_index < 0:
        raise ValueError("start_index must be non-negative")
    variants = [variant for variant in VARIANTS if not (skip_baseline and variant.label == "baseline")]
    return variants[start_index : start_index + max_jobs]


def build_command(
    solver: str,
    input_path: str,
    time_limit: int,
    options: Sequence[str],
    time_bin: str | None = "/usr/bin/time",
    timeout_bin: str | None = "timeout",
) -> list[str]:
    command: list[str] = []
    if time_bin:
        command.extend((time_bin, "-v"))
    if timeout_bin:
        command.extend((timeout_bin, str(time_limit)))
    command.append(solver)
    command.extend(options)
    command.append(input_path)
    return command


def write_manifest(path: Path, records: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, sort_keys=True))
            output.write("\n")


def launch_portfolio(args: argparse.Namespace) -> list[dict[str, object]]:
    variants = select_variants(args.max_jobs, skip_baseline=args.skip_baseline, start_index=args.start_index)
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    for variant in variants:
        log_path = log_dir / f"{args.prefix}_{variant.label}.log"
        command = build_command(
            args.solver,
            args.input,
            args.time_limit,
            variant.options,
            time_bin=args.time_bin,
            timeout_bin=args.timeout_bin,
        )
        record: dict[str, object] = {
            "label": variant.label,
            "pid": None,
            "log": str(log_path),
            "options": list(variant.options),
            "command": command,
        }
        if not args.dry_run:
            with log_path.open("wb") as log_file:
                process = subprocess.Popen(
                    command,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            record["pid"] = process.pid
        records.append(record)

    write_manifest(Path(args.manifest), records)
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch a CaDiCaL portfolio for an E_m DIMACS CNF.")
    parser.add_argument("--solver", default="artifacts/solvers/cadical_pkg/usr/bin/cadical")
    parser.add_argument("--input", default="artifacts/problem835_e1.cnf")
    parser.add_argument("--time-limit", type=int, default=1800)
    parser.add_argument("--max-jobs", type=int, default=5)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--log-dir", default="artifacts/solver_logs")
    parser.add_argument("--prefix", default="cadical_portfolio")
    parser.add_argument("--manifest", default="artifacts/solver_logs/cadical_portfolio.jsonl")
    parser.add_argument("--time-bin", default="/usr/bin/time", help="set empty to disable /usr/bin/time wrapper")
    parser.add_argument("--timeout-bin", default="timeout", help="set empty to disable timeout wrapper")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.time_bin == "":
        args.time_bin = None
    if args.timeout_bin == "":
        args.timeout_bin = None

    records = launch_portfolio(args)
    for record in records:
        pid = record["pid"] if record["pid"] is not None else "dry-run"
        print(f"{pid}\t{record['label']}\t{record['log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
