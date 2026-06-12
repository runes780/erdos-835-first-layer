from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable, Iterator, TextIO

from src.erdos835_one_color import OneColorConfig
from src.extension_ladder import (
    _forced_ladder_rows,
    _parse_block_text,
    _iter_d_star_constraints,
    _iter_disjointness_constraints,
    _iter_point_extension_constraints,
    build_extension_ladder_row_index,
)


Clause = tuple[int, ...]


@dataclass(frozen=True)
class ExtensionLadderCnfStats:
    variables: int
    base_variables: int
    auxiliary_variables: int
    exact_one_constraints: int
    exact_one_clauses: int
    disjointness_clauses: int
    symmetry_unit_clauses: int
    d3_upper_constraints: int
    d3_upper_clauses: int
    g4_upper_constraints: int
    g4_upper_clauses: int
    extra_upper_constraints: int
    extra_upper_clauses: int
    total_clauses: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def _pairwise_exact_one_clause_count(length: int) -> int:
    return 1 + comb(length, 2)


def _sequential_aux_count(length: int, bound: int) -> int:
    if bound < 0:
        raise ValueError("upper bound must be nonnegative")
    if length <= bound:
        return 0
    if length == 0 or bound == 0:
        return 0
    return (length - 1) * bound


def _sequential_clause_count(length: int, bound: int) -> int:
    if bound < 0:
        raise ValueError("upper bound must be nonnegative")
    if length <= bound:
        return 0
    if bound == 0:
        return length
    if length < 2:
        return 0
    return 2 * (length - 1) + (length - 2) * (2 * bound - 1)


def _sequential_at_most_k_clauses(
    row_ids: Iterable[int],
    bound: int,
    aux_start: int,
) -> Iterator[Clause]:
    ids = tuple(row_ids)
    length = len(ids)
    if bound < 0:
        raise ValueError("upper bound must be nonnegative")
    if length <= bound:
        return
    if bound == 0:
        for row_id in ids:
            yield (-row_id,)
        return

    def aux(index: int, count: int) -> int:
        return aux_start + (index - 1) * bound + (count - 1)

    for index, row_id in enumerate(ids[:-1], start=1):
        yield (-row_id, aux(index, 1))

    for index in range(2, length):
        for count in range(1, bound + 1):
            yield (-aux(index - 1, count), aux(index, count))

    for index, row_id in enumerate(ids[1:], start=2):
        yield (-row_id, -aux(index - 1, bound))

    for index, row_id in enumerate(ids[1:-1], start=2):
        for count in range(2, bound + 1):
            yield (-row_id, -aux(index - 1, count - 1), aux(index, count))


def _require_problem_835_upper_counts(config: OneColorConfig, option: str) -> None:
    if config.v != 21 or config.t != 4:
        raise ValueError(f"{option} is currently implemented only for v=21,t=4")


def _d3_upper_count_stats(config: OneColorConfig) -> tuple[int, int, int]:
    _require_problem_835_upper_counts(config, "--add-d3-upper-counts")
    constraints = comb(config.v, 3)
    length = comb(config.v - 3, config.t + 1 - 3)
    bound = 9
    return (
        constraints,
        constraints * _sequential_aux_count(length, bound),
        constraints * _sequential_clause_count(length, bound),
    )


def _g4_upper_count_stats(config: OneColorConfig) -> tuple[int, int, int]:
    _require_problem_835_upper_counts(config, "--add-g4-upper-counts")
    constraints = config.extension_count * comb(config.v, 4)
    length = comb(config.v - 4, config.t + 2 - 4)
    bound = 8
    return (
        constraints,
        constraints * _sequential_aux_count(length, bound),
        constraints * _sequential_clause_count(length, bound),
    )


def _iter_d3_upper_count_constraints(
    config: OneColorConfig,
    d_row_id_by_block: dict[tuple[int, ...], int],
) -> Iterator[tuple[int, tuple[int, ...]]]:
    _require_problem_835_upper_counts(config, "--add-d3-upper-counts")
    for subset in combinations(range(config.v), 3):
        subset_set = set(subset)
        row_ids = []
        for extension in combinations((point for point in range(config.v) if point not in subset_set), 2):
            block = tuple(sorted((*subset, *extension)))
            row_ids.append(d_row_id_by_block[block])
        yield (9, tuple(row_ids))


def _iter_g4_upper_count_constraints(
    config: OneColorConfig,
    x_row_id_by_key: dict[tuple[int, tuple[int, ...]], int],
) -> Iterator[tuple[int, tuple[int, ...]]]:
    _require_problem_835_upper_counts(config, "--add-g4-upper-counts")
    for family in range(config.extension_count):
        for subset in combinations(range(config.v), 4):
            subset_set = set(subset)
            row_ids = []
            for extension in combinations((point for point in range(config.v) if point not in subset_set), 2):
                block = tuple(sorted((*subset, *extension)))
                row_ids.append(x_row_id_by_key[(family, block)])
            yield (8, tuple(row_ids))


def compute_extension_ladder_cnf_stats(
    config: OneColorConfig,
    symmetry_break: str | None = None,
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
    add_d3_upper_counts: bool = False,
    add_g4_upper_counts: bool = False,
    extra_upper_bounds: Iterable[tuple[Iterable[int], int]] | None = None,
) -> ExtensionLadderCnfStats:
    """Return DIMACS CNF counts for pairwise encoding of the E_m model."""

    config.validate()
    forced_rows = _forced_ladder_rows(config, symmetry_break, forced_d_blocks)

    d_rows = comb(config.v, config.t + 1)
    u_rows = comb(config.v, config.t + 2)
    base_variables = d_rows + config.extension_count * u_rows
    exact_one_constraints = comb(config.v, config.t) + config.extension_count * d_rows
    exact_one_length = config.v - config.t
    exact_one_clauses = exact_one_constraints * _pairwise_exact_one_clause_count(exact_one_length)
    disjointness_clauses = 0
    if config.extension_count >= 2:
        disjointness_clauses = u_rows * comb(config.extension_count, 2)
    symmetry_unit_clauses = len(forced_rows)

    auxiliary_variables = 0
    d3_upper_constraints = d3_upper_clauses = 0
    if add_d3_upper_counts:
        d3_upper_constraints, d3_auxiliary_variables, d3_upper_clauses = _d3_upper_count_stats(config)
        auxiliary_variables += d3_auxiliary_variables

    g4_upper_constraints = g4_upper_clauses = 0
    if add_g4_upper_counts:
        g4_upper_constraints, g4_auxiliary_variables, g4_upper_clauses = _g4_upper_count_stats(config)
        auxiliary_variables += g4_auxiliary_variables

    extra_upper_constraints = extra_upper_clauses = 0
    for row_ids, bound in extra_upper_bounds or ():
        length = len(tuple(row_ids))
        extra_upper_constraints += 1
        auxiliary_variables += _sequential_aux_count(length, bound)
        extra_upper_clauses += _sequential_clause_count(length, bound)

    return ExtensionLadderCnfStats(
        variables=base_variables + auxiliary_variables,
        base_variables=base_variables,
        auxiliary_variables=auxiliary_variables,
        exact_one_constraints=exact_one_constraints,
        exact_one_clauses=exact_one_clauses,
        disjointness_clauses=disjointness_clauses,
        symmetry_unit_clauses=symmetry_unit_clauses,
        d3_upper_constraints=d3_upper_constraints,
        d3_upper_clauses=d3_upper_clauses,
        g4_upper_constraints=g4_upper_constraints,
        g4_upper_clauses=g4_upper_clauses,
        extra_upper_constraints=extra_upper_constraints,
        extra_upper_clauses=extra_upper_clauses,
        total_clauses=(
            exact_one_clauses
            + disjointness_clauses
            + symmetry_unit_clauses
            + d3_upper_clauses
            + g4_upper_clauses
            + extra_upper_clauses
        ),
    )


def format_extension_ladder_cnf_stats(stats: ExtensionLadderCnfStats) -> str:
    return "\n".join(
        [
            f"variables: {stats.variables}",
            f"base variables: {stats.base_variables}",
            f"auxiliary variables: {stats.auxiliary_variables}",
            f"exact-one constraints: {stats.exact_one_constraints}",
            f"exact-one clauses: {stats.exact_one_clauses}",
            f"disjointness clauses: {stats.disjointness_clauses}",
            f"symmetry unit clauses: {stats.symmetry_unit_clauses}",
            f"D3 upper-count constraints: {stats.d3_upper_constraints}",
            f"D3 upper-count clauses: {stats.d3_upper_clauses}",
            f"G4 upper-count constraints: {stats.g4_upper_constraints}",
            f"G4 upper-count clauses: {stats.g4_upper_clauses}",
            f"extra upper-bound constraints: {stats.extra_upper_constraints}",
            f"extra upper-bound clauses: {stats.extra_upper_clauses}",
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
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
    add_d3_upper_counts: bool = False,
    add_g4_upper_counts: bool = False,
    extra_upper_bounds: Iterable[tuple[Iterable[int], int]] | None = None,
) -> Iterator[Clause]:
    """Yield DIMACS clauses for the staged E_m pairwise CNF encoding."""

    config.validate()
    forced_rows = _forced_ladder_rows(config, symmetry_break, forced_d_blocks)
    row_names, d_row_id_by_block, x_row_id_by_key = build_extension_ladder_row_index(config)
    row_id_by_name = {row_name: row_id for row_id, row_name in enumerate(row_names, start=1)}
    next_aux_id = len(row_names) + 1

    for _, row_ids in _iter_d_star_constraints(config, d_row_id_by_block):
        yield from _exact_one_clauses(row_ids)

    for _, row_ids in _iter_point_extension_constraints(config, d_row_id_by_block, x_row_id_by_key):
        yield from _exact_one_clauses(row_ids)

    for _, row_ids in _iter_disjointness_constraints(config, x_row_id_by_key):
        yield from _at_most_one_clauses(row_ids)

    for row_name in forced_rows:
        yield (row_id_by_name[row_name],)

    if add_d3_upper_counts:
        for bound, row_ids in _iter_d3_upper_count_constraints(config, d_row_id_by_block):
            yield from _sequential_at_most_k_clauses(row_ids, bound, next_aux_id)
            next_aux_id += _sequential_aux_count(len(row_ids), bound)

    if add_g4_upper_counts:
        for bound, row_ids in _iter_g4_upper_count_constraints(config, x_row_id_by_key):
            yield from _sequential_at_most_k_clauses(row_ids, bound, next_aux_id)
            next_aux_id += _sequential_aux_count(len(row_ids), bound)

    for row_ids, bound in extra_upper_bounds or ():
        ids = tuple(row_ids)
        yield from _sequential_at_most_k_clauses(ids, bound, next_aux_id)
        next_aux_id += _sequential_aux_count(len(ids), bound)


def _write_clause(output: TextIO, clause: Clause) -> None:
    output.write(" ".join(str(literal) for literal in clause))
    output.write(" 0\n")


def write_extension_ladder_cnf(
    config: OneColorConfig,
    output: TextIO,
    symmetry_break: str | None = None,
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
    add_d3_upper_counts: bool = False,
    add_g4_upper_counts: bool = False,
    extra_upper_bounds: Iterable[tuple[Iterable[int], int]] | None = None,
) -> None:
    """Write a DIMACS CNF file using pairwise exact-one constraints."""

    extra_upper_bounds = tuple((tuple(row_ids), bound) for row_ids, bound in (extra_upper_bounds or ()))
    stats = compute_extension_ladder_cnf_stats(
        config,
        symmetry_break=symmetry_break,
        forced_d_blocks=forced_d_blocks,
        add_d3_upper_counts=add_d3_upper_counts,
        add_g4_upper_counts=add_g4_upper_counts,
        extra_upper_bounds=extra_upper_bounds,
    )
    output.write(f"p cnf {stats.variables} {stats.total_clauses}\n")
    for clause in iter_extension_ladder_cnf_clauses(
        config,
        symmetry_break=symmetry_break,
        forced_d_blocks=forced_d_blocks,
        add_d3_upper_counts=add_d3_upper_counts,
        add_g4_upper_counts=add_g4_upper_counts,
        extra_upper_bounds=extra_upper_bounds,
    ):
        _write_clause(output, clause)


def export_extension_ladder_cnf(
    config: OneColorConfig,
    symmetry_break: str | None = None,
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
    add_d3_upper_counts: bool = False,
    add_g4_upper_counts: bool = False,
    extra_upper_bounds: Iterable[tuple[Iterable[int], int]] | None = None,
) -> str:
    """Return DIMACS text for tests and toy instances."""

    from io import StringIO

    buffer = StringIO()
    write_extension_ladder_cnf(
        config,
        buffer,
        symmetry_break=symmetry_break,
        forced_d_blocks=forced_d_blocks,
        add_d3_upper_counts=add_d3_upper_counts,
        add_g4_upper_counts=add_g4_upper_counts,
        extra_upper_bounds=extra_upper_bounds,
    )
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
    parser.add_argument(
        "--force-d-block",
        action="append",
        default=[],
        metavar="POINTS",
        help="force one D block, e.g. 0,1,3,6,8; may be repeated",
    )
    parser.add_argument(
        "--add-d3-upper-counts",
        action="store_true",
        help="add problem-835 redundant D3 <= 9 sequential-counter constraints",
    )
    parser.add_argument(
        "--add-g4-upper-counts",
        action="store_true",
        help="add problem-835 redundant G4 <= 8 sequential-counter constraints",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = OneColorConfig(v=args.v, t=args.t, extension_count=args.extension_count)
    symmetry_break = None if args.symmetry_break == "none" else args.symmetry_break
    forced_d_blocks = [_parse_block_text(text) for text in args.force_d_block]

    if args.command == "stats":
        stats = compute_extension_ladder_cnf_stats(
            config,
            symmetry_break=symmetry_break,
            forced_d_blocks=forced_d_blocks,
            add_d3_upper_counts=args.add_d3_upper_counts,
            add_g4_upper_counts=args.add_g4_upper_counts,
        )
        if args.json:
            print(json.dumps(stats.to_dict(), indent=2, sort_keys=True))
        else:
            print(format_extension_ladder_cnf_stats(stats))
        return 0

    if args.command == "cnf":
        if args.output is None:
            import sys

            write_extension_ladder_cnf(
                config,
                sys.stdout,
                symmetry_break=symmetry_break,
                forced_d_blocks=forced_d_blocks,
                add_d3_upper_counts=args.add_d3_upper_counts,
                add_g4_upper_counts=args.add_g4_upper_counts,
            )
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8", newline="\n") as output:
                write_extension_ladder_cnf(
                    config,
                    output,
                    symmetry_break=symmetry_break,
                    forced_d_blocks=forced_d_blocks,
                    add_d3_upper_counts=args.add_d3_upper_counts,
                    add_g4_upper_counts=args.add_g4_upper_counts,
                )
        return 0

    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
