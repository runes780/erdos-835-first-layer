from __future__ import annotations

import argparse
import json
from pathlib import Path
from dataclasses import asdict, dataclass
from itertools import combinations
from math import comb
from typing import Iterable, Iterator, TextIO


Block = tuple[int, ...]
ExactCoverRow = tuple[str, tuple[str, ...]]


@dataclass(frozen=True)
class OneColorConfig:
    """Parameters for the one-color exact-cover shadow instance.

    The #835 first-layer case is v=21, t=4, extension_count=11.  The
    one-color D-blocks then have size t+1=5, while the G-blocks have
    size t+2=6.
    """

    v: int
    t: int
    extension_count: int

    @classmethod
    def problem_835(cls) -> "OneColorConfig":
        return cls(v=21, t=4, extension_count=11)

    @property
    def d_size(self) -> int:
        return self.t + 1

    @property
    def u_size(self) -> int:
        return self.t + 2

    def validate(self) -> None:
        if self.v <= 0:
            raise ValueError("v must be positive")
        if self.t < 0:
            raise ValueError("t must be non-negative")
        if self.extension_count <= 0:
            raise ValueError("extension_count must be positive")
        if self.u_size > self.v:
            raise ValueError("need t+2 <= v")


@dataclass(frozen=True)
class OneColorStats:
    d_rows: int
    x_rows: int
    total_rows: int
    t_columns: int
    pair_columns: int
    u_columns: int
    total_columns: int
    d_row_incidences: int
    x_row_incidences: int
    total_incidences: int
    constraint_lengths: tuple[int, int, int]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def comb_tuples(n: int, k: int) -> list[Block]:
    """Return lexicographic k-subsets of {0,...,n-1} as sorted tuples."""
    if k < 0 or k > n:
        return []
    return list(combinations(range(n), k))


def iter_comb_tuples(n: int, k: int) -> Iterator[Block]:
    """Yield lexicographic k-subsets of {0,...,n-1} as sorted tuples."""
    return combinations(range(n), k)


def format_block(block: Block) -> str:
    return ",".join(str(point) for point in block)


def _column(kind: str, block: Block, j: int | None = None) -> str:
    prefix = kind if j is None else f"{kind}:{j}"
    return f"{prefix}:{format_block(block)}"


def _extensions(block: Block, v: int) -> Iterator[Block]:
    block_set = set(block)
    for point in range(v):
        if point not in block_set:
            yield tuple(sorted((*block, point)))


def iter_exact_cover_rows(config: OneColorConfig) -> Iterator[ExactCoverRow]:
    """Yield sparse exact-cover rows as ``(row_name, column_names)``.

    A D-row represents selecting one (t+1)-block S in the one-color design.
    An X-row represents selecting one pair (j,U), where U is a (t+2)-block in
    the j-th extension family.  The row order is lexicographic and stable.
    """

    config.validate()
    v = config.v
    t = config.t
    m = config.extension_count

    for s_block in iter_comb_tuples(v, t + 1):
        columns: list[str] = []
        columns.extend(_column("T", subblock) for subblock in combinations(s_block, t))
        columns.extend(_column("P", s_block, j) for j in range(m))
        columns.extend(_column("U", u_block) for u_block in _extensions(s_block, v))
        yield (f"D:{format_block(s_block)}", tuple(columns))

    for j in range(m):
        for u_block in iter_comb_tuples(v, t + 2):
            columns = [_column("P", subblock, j) for subblock in combinations(u_block, t + 1)]
            columns.append(_column("U", u_block))
            yield (f"X:{j}:{format_block(u_block)}", tuple(columns))


def build_column_index(config: OneColorConfig) -> tuple[list[str], dict[str, list[int]]]:
    """Invert sparse rows to exact-one columns.

    Row ids are one-based, matching OPB variable names x1, x2, ...
    """

    row_names: list[str] = []
    column_index: dict[str, list[int]] = {}

    for row_id, (row_name, columns) in enumerate(iter_exact_cover_rows(config), start=1):
        row_names.append(row_name)
        for column in columns:
            column_index.setdefault(column, []).append(row_id)

    return row_names, column_index


def write_opb(config: OneColorConfig, output: TextIO, include_row_comments: bool = True) -> None:
    """Write the exact-cover system in OPB pseudo-Boolean format."""

    row_names, column_index = build_column_index(config)
    output.write(f"* #variable= {len(row_names)} #constraint= {len(column_index)}\n")

    if include_row_comments:
        for row_id, row_name in enumerate(row_names, start=1):
            output.write(f"* row {row_id} {row_name}\n")

    for column, row_ids in column_index.items():
        terms = " ".join(f"+1 x{row_id}" for row_id in row_ids)
        output.write(f"{terms} = 1 ; * {column}\n")


def export_opb(config: OneColorConfig, include_row_comments: bool = True) -> str:
    """Return OPB text.  Intended for tests and small instances."""

    from io import StringIO

    buffer = StringIO()
    write_opb(config, buffer, include_row_comments=include_row_comments)
    return buffer.getvalue()


def normalize_block(block: Iterable[int], expected_size: int, v: int) -> Block:
    normalized = tuple(sorted(block))
    if len(normalized) != expected_size:
        raise ValueError(f"block {normalized} has size {len(normalized)}, expected {expected_size}")
    if len(set(normalized)) != expected_size:
        raise ValueError(f"block {normalized} has repeated points")
    if normalized and (normalized[0] < 0 or normalized[-1] >= v):
        raise ValueError(f"block {normalized} is outside point set 0..{v - 1}")
    return normalized


def compute_stats(config: OneColorConfig) -> OneColorStats:
    config.validate()
    v = config.v
    t = config.t
    m = config.extension_count

    d_rows = comb(v, t + 1)
    u_columns = comb(v, t + 2)
    x_rows = m * u_columns

    t_columns = comb(v, t)
    pair_columns = m * d_rows
    total_columns = t_columns + pair_columns + u_columns
    total_rows = d_rows + x_rows

    d_row_size = comb(t + 1, t) + m + (v - (t + 1))
    x_row_size = comb(t + 2, t + 1) + 1
    d_row_incidences = d_rows * d_row_size
    x_row_incidences = x_rows * x_row_size

    constraint_lengths = (
        v - t,
        v - t,
        m + t + 2,
    )

    return OneColorStats(
        d_rows=d_rows,
        x_rows=x_rows,
        total_rows=total_rows,
        t_columns=t_columns,
        pair_columns=pair_columns,
        u_columns=u_columns,
        total_columns=total_columns,
        d_row_incidences=d_row_incidences,
        x_row_incidences=x_row_incidences,
        total_incidences=d_row_incidences + x_row_incidences,
        constraint_lengths=constraint_lengths,
    )


def format_stats(stats: OneColorStats) -> str:
    lines = [
        f"D rows: {stats.d_rows}",
        f"x rows: {stats.x_rows}",
        f"total rows: {stats.total_rows}",
        f"t-subset columns: {stats.t_columns}",
        f"(j,S) columns: {stats.pair_columns}",
        f"U-shadow columns: {stats.u_columns}",
        f"total columns: {stats.total_columns}",
        f"D row incidences: {stats.d_row_incidences}",
        f"x row incidences: {stats.x_row_incidences}",
        f"total incidences: {stats.total_incidences}",
        f"constraint lengths: {stats.constraint_lengths}",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["stats", "rows", "opb"], help="operation to run")
    parser.add_argument("--v", type=int, default=21, help="number of points")
    parser.add_argument("--t", type=int, default=4, help="D design strength")
    parser.add_argument("--extension-count", type=int, default=11, help="number of G families")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--limit", type=int, default=None, help="only emit the first N rows")
    parser.add_argument("--output", type=Path, default=None, help="write output to this path")
    parser.add_argument("--no-row-comments", action="store_true", help="omit OPB row-name comments")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = OneColorConfig(v=args.v, t=args.t, extension_count=args.extension_count)

    if args.command == "stats":
        stats = compute_stats(config)
        if args.json:
            print(json.dumps(stats.to_dict(), indent=2, sort_keys=True))
        else:
            print(format_stats(stats))
        return 0

    if args.command == "rows":
        for index, (row_name, columns) in enumerate(iter_exact_cover_rows(config)):
            if args.limit is not None and index >= args.limit:
                break
            print(" ".join((row_name, *columns)))
        return 0

    if args.command == "opb":
        if args.limit is not None:
            raise SystemExit("--limit is not supported for OPB export")
        include_row_comments = not args.no_row_comments
        if args.output is None:
            import sys

            write_opb(config, sys.stdout, include_row_comments=include_row_comments)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8") as output:
                write_opb(config, output, include_row_comments=include_row_comments)
        return 0

    raise AssertionError(f"unhandled command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
