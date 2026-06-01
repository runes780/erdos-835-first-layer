from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable, Iterator, TextIO

from src.erdos835_one_color import OneColorConfig, forced_symmetry_break_rows
from src.extension_ladder import (
    _iter_d_star_constraints,
    _iter_disjointness_constraints,
    _iter_point_extension_constraints,
    build_extension_ladder_row_index,
)


Clause = tuple[int, ...]


@dataclass(frozen=True)
class ExtensionLadderCnfStats:
    variables: int
    exact_one_constraints: int
    exact_one_clauses: int
    disjointness_clauses: int
    symmetry_unit_clauses: int
    total_clauses: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def _pairwise_exact_one_clause_count(length: int) -> int:
    return 1 + comb(length, 2)


def compute_extension_ladder_cnf_stats(
    config: OneColorConfig,
    symmetry_break: str | None = None,
) -> ExtensionLadderCnfStats:
    """Return DIMACS CNF counts for pairwise encoding of the E_m model."""

    config.validate()
    forced_rows = forced_symmetry_break_rows(config, symmetry_break)

    d_rows = comb(config.v, config.t + 1)
    u_rows = comb(config.v, config.t + 2)
    variables = d_rows + config.extension_count * u_rows
    exact_one_constraints = comb(config.v, config.t) + config.extension_count * d_rows
    exact_one_length = config.v - config.t
    exact_one_clauses = exact_one_constraints * _pairwise_exact_one_clause_count(exact_one_length)
    disjointness_clauses = 0
    if config.extension_count >= 2:
        disjointness_clauses = u_rows * comb(config.extension_count, 2)
    symmetry_unit_clauses = len(forced_rows)

    return ExtensionLadderCnfStats(
        variables=variables,
        exact_one_constraints=exact_one_constraints,
        exact_one_clauses=exact_one_clauses,
        disjointness_clauses=disjointness_clauses,
        symmetry_unit_clauses=symmetry_unit_clauses,
        total_clauses=exact_one_clauses + disjointness_clauses + symmetry_unit_clauses,
    )


def format_extension_ladder_cnf_stats(stats: ExtensionLadderCnfStats) -> str:
    return "\n".join(
        [
            f"variables: {stats.variables}",
            f"exact-one constraints: {stats.exact_one_constraints}",
            f"exact-one clauses: {stats.exact_one_clauses}",
            f"disjointness clauses: {stats.disjointness_clauses}",
            f"symmetry unit clauses: {stats.symmetry_unit_clauses}",
            f"total clauses: {stats.total_clauses}",
        ]
    )


def _exact_one_clauses(row_ids: Iterable[int]) -> Iterator[Clause]:
    ids = tuple(row_ids)
    yield ids
    for left, right in combinations(ids, 2):
        yield (-left, -right)


def _at_most_one_clauses(row_ids: Iterable[int]) -> Iterator[Clause]:
    for left, right in combinations(tuple(row_ids), 2):
        yield (-left, -right)


def iter_extension_ladder_cnf_clauses(
    config: OneColorConfig,
    symmetry_break: str | None = None,
) -> Iterator[Clause]:
    """Yield DIMACS clauses for the staged E_m pairwise CNF encoding."""

    config.validate()
    forced_rows = forced_symmetry_break_rows(config, symmetry_break)
    row_names, d_row_id_by_block, x_row_id_by_key = build_extension_ladder_row_index(config)
    row_id_by_name = {row_name: row_id for row_id, row_name in enumerate(row_names, start=1)}

    for _, row_ids in _iter_d_star_constraints(config, d_row_id_by_block):
        yield from _exact_one_clauses(row_ids)

    for _, row_ids in _iter_point_extension_constraints(config, d_row_id_by_block, x_row_id_by_key):
        yield from _exact_one_clauses(row_ids)

    for _, row_ids in _iter_disjointness_constraints(config, x_row_id_by_key):
        yield from _at_most_one_clauses(row_ids)

    for row_name in forced_rows:
        yield (row_id_by_name[row_name],)


def _write_clause(output: TextIO, clause: Clause) -> None:
    output.write(" ".join(str(literal) for literal in clause))
    output.write(" 0\n")


def write_extension_ladder_cnf(
    config: OneColorConfig,
    output: TextIO,
    symmetry_break: str | None = None,
) -> None:
    """Write a DIMACS CNF file using pairwise exact-one constraints."""

    stats = compute_extension_ladder_cnf_stats(config, symmetry_break=symmetry_break)
    output.write(f"p cnf {stats.variables} {stats.total_clauses}\n")
    for clause in iter_extension_ladder_cnf_clauses(config, symmetry_break=symmetry_break):
        _write_clause(output, clause)


def export_extension_ladder_cnf(
    config: OneColorConfig,
    symmetry_break: str | None = None,
) -> str:
    """Return DIMACS text for tests and toy instances."""

    from io import StringIO

    buffer = StringIO()
    write_extension_ladder_cnf(config, buffer, symmetry_break=symmetry_break)
    return buffer.getvalue()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["stats", "cnf"], help="operation to run")
    parser.add_argument("--v", type=int, default=21, help="number of points")
    parser.add_argument("--t", type=int, default=4, help="D design strength")
    parser.add_argument("--extension-count", type=int, default=1, help="number of staged G families")
    parser.add_argument("--json", action="store_true", help="emit JSON for stats")
    parser.add_argument("--output", type=Path, default=None, help="write CNF output to this path")
    parser.add_argument(
        "--symmetry-break",
        choices=["none", "triple-matching", "triple-matching-off-triple"],
        default="none",
        help="append supported symmetry-breaking unit clauses",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = OneColorConfig(v=args.v, t=args.t, extension_count=args.extension_count)
    symmetry_break = None if args.symmetry_break == "none" else args.symmetry_break

    if args.command == "stats":
        stats = compute_extension_ladder_cnf_stats(config, symmetry_break=symmetry_break)
        if args.json:
            print(json.dumps(stats.to_dict(), indent=2, sort_keys=True))
        else:
            print(format_extension_ladder_cnf_stats(stats))
        return 0

    if args.command == "cnf":
        if args.output is None:
            import sys

            write_extension_ladder_cnf(config, sys.stdout, symmetry_break=symmetry_break)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8", newline="\n") as output:
                write_extension_ladder_cnf(config, output, symmetry_break=symmetry_break)
        return 0

    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
