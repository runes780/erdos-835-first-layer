from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable, Iterator, TextIO

from src.erdos835_one_color import (
    Block,
    OneColorConfig,
    _column,
    _d_row_name,
    _d_lower_count_rhs,
    _extensions,
    _g4_count_rhs,
    _iter_d_lower_count_constraints,
    _iter_g4_count_constraints,
    _x_row_name,
    forced_symmetry_break_rows,
    iter_comb_tuples,
    normalize_block,
)


@dataclass(frozen=True)
class ExtensionLadderStats:
    d_rows: int
    x_rows: int
    total_variables: int
    d_star_constraints: int
    point_extension_constraints: int
    exact_one_constraints: int
    disjointness_constraints: int
    total_constraints: int
    d_row_exact_one_incidences: int
    x_row_exact_one_incidences: int
    exact_one_incidences: int
    disjointness_incidences: int
    total_incidences: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def compute_extension_ladder_stats(config: OneColorConfig) -> ExtensionLadderStats:
    """Return row-variable and constraint counts for the staged E_m model."""

    config.validate()
    v = config.v
    t = config.t
    m = config.extension_count

    d_rows = comb(v, t + 1)
    u_rows = comb(v, t + 2)
    x_rows = m * u_rows
    total_variables = d_rows + x_rows

    d_star_constraints = comb(v, t)
    point_extension_constraints = m * d_rows
    exact_one_constraints = d_star_constraints + point_extension_constraints
    disjointness_constraints = u_rows if m >= 2 else 0
    total_constraints = exact_one_constraints + disjointness_constraints

    d_row_exact_one_incidences = d_rows * ((t + 1) + m)
    x_row_exact_one_incidences = x_rows * (t + 2)
    exact_one_incidences = d_row_exact_one_incidences + x_row_exact_one_incidences
    disjointness_incidences = x_rows if m >= 2 else 0
    total_incidences = exact_one_incidences + disjointness_incidences

    return ExtensionLadderStats(
        d_rows=d_rows,
        x_rows=x_rows,
        total_variables=total_variables,
        d_star_constraints=d_star_constraints,
        point_extension_constraints=point_extension_constraints,
        exact_one_constraints=exact_one_constraints,
        disjointness_constraints=disjointness_constraints,
        total_constraints=total_constraints,
        d_row_exact_one_incidences=d_row_exact_one_incidences,
        x_row_exact_one_incidences=x_row_exact_one_incidences,
        exact_one_incidences=exact_one_incidences,
        disjointness_incidences=disjointness_incidences,
        total_incidences=total_incidences,
    )


def format_extension_ladder_stats(stats: ExtensionLadderStats) -> str:
    return "\n".join(
        [
            f"D rows: {stats.d_rows}",
            f"x rows: {stats.x_rows}",
            f"total variables: {stats.total_variables}",
            f"D-star constraints: {stats.d_star_constraints}",
            f"point-extension constraints: {stats.point_extension_constraints}",
            f"exact-one constraints: {stats.exact_one_constraints}",
            f"disjointness constraints: {stats.disjointness_constraints}",
            f"total constraints: {stats.total_constraints}",
            f"D exact-one incidences: {stats.d_row_exact_one_incidences}",
            f"x exact-one incidences: {stats.x_row_exact_one_incidences}",
            f"exact-one incidences: {stats.exact_one_incidences}",
            f"disjointness incidences: {stats.disjointness_incidences}",
            f"total incidences: {stats.total_incidences}",
        ]
    )


def build_extension_ladder_row_index(
    config: OneColorConfig,
) -> tuple[list[str], dict[Block, int], dict[tuple[int, Block], int]]:
    """Return stable row names and one-based OPB ids for D and X rows."""

    config.validate()
    row_names: list[str] = []
    d_row_id_by_block: dict[Block, int] = {}
    x_row_id_by_key: dict[tuple[int, Block], int] = {}

    for s_block in iter_comb_tuples(config.v, config.t + 1):
        row_names.append(_d_row_name(s_block))
        d_row_id_by_block[s_block] = len(row_names)

    for j in range(config.extension_count):
        for u_block in iter_comb_tuples(config.v, config.t + 2):
            row_names.append(_x_row_name(j, u_block))
            x_row_id_by_key[(j, u_block)] = len(row_names)

    return row_names, d_row_id_by_block, x_row_id_by_key


def _parse_block_text(text: str) -> Block:
    try:
        return tuple(int(part) for part in text.split(",") if part != "")
    except ValueError as exc:
        raise ValueError(f"invalid block {text!r}") from exc


def _forced_ladder_rows(
    config: OneColorConfig,
    symmetry_break: str | None,
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
) -> tuple[str, ...]:
    rows: list[str] = list(forced_symmetry_break_rows(config, symmetry_break))
    for block in forced_d_blocks or ():
        rows.append(_d_row_name(normalize_block(block, config.t + 1, config.v)))
    return tuple(dict.fromkeys(rows))


def _write_pb_constraint(
    output: TextIO,
    row_ids: Iterable[int],
    operator: str,
    rhs: int,
    comment: str,
    include_comment: bool,
) -> None:
    terms = " ".join(f"+1 x{row_id}" for row_id in row_ids)
    suffix = f" * {comment}" if include_comment else ""
    output.write(f"{terms} {operator} {rhs} ;{suffix}\n")


def _iter_d_star_constraints(
    config: OneColorConfig,
    d_row_id_by_block: dict[Block, int],
) -> Iterator[tuple[str, tuple[int, ...]]]:
    for t_block in iter_comb_tuples(config.v, config.t):
        t_set = set(t_block)
        row_ids: list[int] = []
        for extra in (point for point in range(config.v) if point not in t_set):
            s_block = tuple(sorted((*t_block, extra)))
            row_ids.append(d_row_id_by_block[s_block])
        yield (_column("T", t_block), tuple(row_ids))


def _iter_point_extension_constraints(
    config: OneColorConfig,
    d_row_id_by_block: dict[Block, int],
    x_row_id_by_key: dict[tuple[int, Block], int],
) -> Iterator[tuple[str, tuple[int, ...]]]:
    for j in range(config.extension_count):
        for s_block in iter_comb_tuples(config.v, config.t + 1):
            row_ids = [d_row_id_by_block[s_block]]
            row_ids.extend(x_row_id_by_key[(j, u_block)] for u_block in _extensions(s_block, config.v))
            yield (_column("P", s_block, j), tuple(row_ids))


def _iter_disjointness_constraints(
    config: OneColorConfig,
    x_row_id_by_key: dict[tuple[int, Block], int],
) -> Iterator[tuple[str, tuple[int, ...]]]:
    if config.extension_count < 2:
        return
    for u_block in iter_comb_tuples(config.v, config.t + 2):
        row_ids = tuple(x_row_id_by_key[(j, u_block)] for j in range(config.extension_count))
        yield (_column("U", u_block), row_ids)


def write_extension_ladder_opb(
    config: OneColorConfig,
    output: TextIO,
    include_row_comments: bool = True,
    include_column_comments: bool = True,
    symmetry_break: str | None = None,
    add_d_lower_counts: bool = False,
    add_g4_counts: bool = False,
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
) -> None:
    """Write the staged E_m pseudo-Boolean model in OPB format."""

    config.validate()
    forced_rows = _forced_ladder_rows(config, symmetry_break, forced_d_blocks)
    stats = compute_extension_ladder_stats(config)
    extra_constraint_count = len(forced_rows)
    if add_d_lower_counts:
        for r in range(4):
            _d_lower_count_rhs(config, r)
            extra_constraint_count += comb(config.v, r)
    if add_g4_counts:
        _g4_count_rhs(config)
        extra_constraint_count += config.extension_count * comb(config.v, 4)
    constraint_count = stats.total_constraints + extra_constraint_count

    row_names, d_row_id_by_block, x_row_id_by_key = build_extension_ladder_row_index(config)
    row_id_by_name = {row_name: row_id for row_id, row_name in enumerate(row_names, start=1)}

    output.write(f"* #variable= {len(row_names)} #constraint= {constraint_count}\n")

    if include_row_comments:
        for row_id, row_name in enumerate(row_names, start=1):
            output.write(f"* row {row_id} {row_name}\n")

    for name, row_ids in _iter_d_star_constraints(config, d_row_id_by_block):
        _write_pb_constraint(output, row_ids, "=", 1, name, include_column_comments)

    for name, row_ids in _iter_point_extension_constraints(config, d_row_id_by_block, x_row_id_by_key):
        _write_pb_constraint(output, row_ids, "=", 1, name, include_column_comments)

    for name, row_ids in _iter_disjointness_constraints(config, x_row_id_by_key):
        _write_pb_constraint(output, row_ids, "<=", 1, name, include_column_comments)

    for row_name in forced_rows:
        _write_pb_constraint(
            output,
            (row_id_by_name[row_name],),
            "=",
            1,
            f"force:{row_name}",
            include_column_comments,
        )

    if add_d_lower_counts:
        for name, row_ids, rhs in _iter_d_lower_count_constraints(config, row_id_by_name):
            _write_pb_constraint(output, row_ids, "=", rhs, name, include_column_comments)

    if add_g4_counts:
        for name, row_ids, rhs in _iter_g4_count_constraints(config, row_id_by_name):
            _write_pb_constraint(output, row_ids, "=", rhs, name, include_column_comments)


def export_extension_ladder_opb(
    config: OneColorConfig,
    include_row_comments: bool = True,
    include_column_comments: bool = True,
    symmetry_break: str | None = None,
    add_d_lower_counts: bool = False,
    add_g4_counts: bool = False,
    forced_d_blocks: Iterable[Iterable[int]] | None = None,
) -> str:
    """Return OPB text for tests and small toy instances."""

    from io import StringIO

    buffer = StringIO()
    write_extension_ladder_opb(
        config,
        buffer,
        include_row_comments=include_row_comments,
        include_column_comments=include_column_comments,
        symmetry_break=symmetry_break,
        add_d_lower_counts=add_d_lower_counts,
        add_g4_counts=add_g4_counts,
        forced_d_blocks=forced_d_blocks,
    )
    return buffer.getvalue()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["stats", "opb"], help="operation to run")
    parser.add_argument("--v", type=int, default=21, help="number of points")
    parser.add_argument("--t", type=int, default=4, help="D design strength")
    parser.add_argument("--extension-count", type=int, default=1, help="number of staged G families")
    parser.add_argument("--json", action="store_true", help="emit JSON for stats")
    parser.add_argument("--output", type=Path, default=None, help="write OPB output to this path")
    parser.add_argument("--no-comments", action="store_true", help="omit all non-header OPB comments")
    parser.add_argument("--no-row-comments", action="store_true", help="omit OPB row-name comments")
    parser.add_argument("--no-column-comments", action="store_true", help="omit OPB column-name comments")
    parser.add_argument(
        "--symmetry-break",
        choices=["none", "triple-matching", "triple-matching-off-triple"],
        default="none",
        help="append supported symmetry-breaking unit constraints",
    )
    parser.add_argument(
        "--add-d-lower-counts",
        action="store_true",
        help="append redundant D lower-subset count constraints for r=0,1,2,3",
    )
    parser.add_argument(
        "--add-g4-counts",
        action="store_true",
        help="append redundant G_j 4-set count constraints to the staged ladder OPB",
    )
    parser.add_argument(
        "--force-d-block",
        action="append",
        default=[],
        metavar="POINTS",
        help="force one D block, e.g. 0,1,3,6,8; may be repeated",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = OneColorConfig(v=args.v, t=args.t, extension_count=args.extension_count)

    if args.command == "stats":
        stats = compute_extension_ladder_stats(config)
        if args.json:
            print(json.dumps(stats.to_dict(), indent=2, sort_keys=True))
        else:
            print(format_extension_ladder_stats(stats))
        return 0

    if args.command == "opb":
        include_row_comments = not (args.no_comments or args.no_row_comments)
        include_column_comments = not (args.no_comments or args.no_column_comments)
        symmetry_break = None if args.symmetry_break == "none" else args.symmetry_break
        forced_d_blocks = [_parse_block_text(text) for text in args.force_d_block]
        if args.output is None:
            import sys

            write_extension_ladder_opb(
                config,
                sys.stdout,
                include_row_comments=include_row_comments,
                include_column_comments=include_column_comments,
                symmetry_break=symmetry_break,
                add_d_lower_counts=args.add_d_lower_counts,
                add_g4_counts=args.add_g4_counts,
                forced_d_blocks=forced_d_blocks,
            )
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8") as output:
                write_extension_ladder_opb(
                    config,
                    output,
                    include_row_comments=include_row_comments,
                    include_column_comments=include_column_comments,
                    symmetry_break=symmetry_break,
                    add_d_lower_counts=args.add_d_lower_counts,
                    add_g4_counts=args.add_g4_counts,
                    forced_d_blocks=forced_d_blocks,
                )
        return 0

    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
