from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Iterable, TextIO

from src.erdos835_one_color import (
    Block,
    OneColorConfig,
    _column,
    _write_pb_equality,
    format_block,
    iter_comb_tuples,
)


@dataclass(frozen=True)
class ConditionalStats:
    variables: int
    constraints: int
    incidences: int


def compute_conditional_stats(
    config: OneColorConfig,
    *,
    d_block_count: int,
    allowed_u_count: int,
) -> ConditionalStats:
    non_d_five_sets = comb(config.v, config.t + 1) - d_block_count
    variables = config.extension_count * allowed_u_count
    constraints = config.extension_count * non_d_five_sets + allowed_u_count
    incidences = variables * (config.t + 3)
    return ConditionalStats(variables=variables, constraints=constraints, incidences=incidences)


def _x_row_name(j: int, block: Block) -> str:
    return f"X:{j}:{format_block(block)}"


def allowed_u_blocks(config: OneColorConfig, d_blocks: Iterable[Block]) -> list[Block]:
    d_set = {tuple(sorted(block)) for block in d_blocks}
    allowed: list[Block] = []
    for u_block in iter_comb_tuples(config.v, config.t + 2):
        if not any(tuple(sorted(s_block)) in d_set for s_block in combinations(u_block, config.t + 1)):
            allowed.append(u_block)
    return allowed


def _non_d_blocks(config: OneColorConfig, d_blocks: set[Block]) -> list[Block]:
    return [s_block for s_block in iter_comb_tuples(config.v, config.t + 1) if s_block not in d_blocks]


def _build_conditional_rows(
    config: OneColorConfig,
    allowed_blocks: list[Block],
) -> tuple[list[str], dict[tuple[int, Block], int]]:
    row_names: list[str] = []
    row_id_by_key: dict[tuple[int, Block], int] = {}
    row_id = 1
    for j in range(config.extension_count):
        for u_block in allowed_blocks:
            row_names.append(_x_row_name(j, u_block))
            row_id_by_key[(j, u_block)] = row_id
            row_id += 1
    return row_names, row_id_by_key


def write_conditional_opb(
    config: OneColorConfig,
    d_blocks: Iterable[Block],
    output: TextIO,
    include_row_comments: bool = True,
    include_column_comments: bool = True,
) -> None:
    config.validate()
    d_set = {tuple(sorted(block)) for block in d_blocks}
    non_d_blocks = _non_d_blocks(config, d_set)
    allowed_blocks = allowed_u_blocks(config, d_set)
    row_names, row_id_by_key = _build_conditional_rows(config, allowed_blocks)

    constraint_count = config.extension_count * len(non_d_blocks) + len(allowed_blocks)
    output.write(f"* #variable= {len(row_names)} #constraint= {constraint_count}\n")

    if include_row_comments:
        for row_id, row_name in enumerate(row_names, start=1):
            output.write(f"* row {row_id} {row_name}\n")

    allowed_by_s: dict[Block, list[Block]] = {s_block: [] for s_block in non_d_blocks}
    for u_block in allowed_blocks:
        for s_block in combinations(u_block, config.t + 1):
            normalized = tuple(sorted(s_block))
            if normalized in allowed_by_s:
                allowed_by_s[normalized].append(u_block)

    for j in range(config.extension_count):
        for s_block in non_d_blocks:
            row_ids = tuple(row_id_by_key[(j, u_block)] for u_block in allowed_by_s[s_block])
            _write_pb_equality(output, row_ids, 1, _column("P", s_block, j), include_column_comments)

    for u_block in allowed_blocks:
        row_ids = tuple(row_id_by_key[(j, u_block)] for j in range(config.extension_count))
        _write_pb_equality(output, row_ids, 1, _column("U", u_block), include_column_comments)


def export_conditional_opb(
    config: OneColorConfig,
    d_blocks: Iterable[Block],
    include_row_comments: bool = True,
    include_column_comments: bool = True,
) -> str:
    from io import StringIO

    buffer = StringIO()
    write_conditional_opb(
        config,
        d_blocks,
        buffer,
        include_row_comments=include_row_comments,
        include_column_comments=include_column_comments,
    )
    return buffer.getvalue()
