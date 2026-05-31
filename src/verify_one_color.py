from __future__ import annotations

from itertools import combinations
from typing import Iterable, Sequence

from .erdos835_one_color import Block, OneColorConfig, iter_comb_tuples, normalize_block


def _subblocks(block: Block, size: int) -> list[Block]:
    return [tuple(subblock) for subblock in combinations(block, size)]


def _normalize_family(blocks: Iterable[Iterable[int]], expected_size: int, v: int) -> tuple[set[Block], list[str]]:
    result: set[Block] = set()
    errors: list[str] = []

    for raw_block in blocks:
        try:
            block = normalize_block(raw_block, expected_size, v)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if block in result:
            errors.append(f"duplicate block {block}")
        result.add(block)

    return result, errors


def verify_one_color(
    config: OneColorConfig,
    d_blocks: Iterable[Iterable[int]],
    g_blocks_by_j: Sequence[Iterable[Iterable[int]]],
) -> list[str]:
    """Check the one-color exact-cover shadow equations.

    Returns a list of human-readable errors.  An empty list means all three
    constraint families are satisfied for the supplied candidate.
    """

    config.validate()
    errors: list[str] = []
    v = config.v
    t = config.t
    m = config.extension_count

    if len(g_blocks_by_j) != m:
        errors.append(f"expected {m} G families, got {len(g_blocks_by_j)}")

    d_family, family_errors = _normalize_family(d_blocks, t + 1, v)
    errors.extend(f"D: {error}" for error in family_errors)

    g_families: list[set[Block]] = []
    for j, raw_family in enumerate(g_blocks_by_j):
        family, family_errors = _normalize_family(raw_family, t + 2, v)
        errors.extend(f"G[{j}]: {error}" for error in family_errors)
        g_families.append(family)

    if errors:
        return errors

    d_by_t: dict[Block, int] = {block: 0 for block in iter_comb_tuples(v, t)}
    for block in d_family:
        for subblock in _subblocks(block, t):
            d_by_t[subblock] += 1

    for subblock, count in d_by_t.items():
        if count != 1:
            errors.append(f"D-star constraint for {subblock} has count {count}, expected 1")

    for j, family in enumerate(g_families):
        g_by_s: dict[Block, int] = {block: 0 for block in iter_comb_tuples(v, t + 1)}
        for block in family:
            for subblock in _subblocks(block, t + 1):
                g_by_s[subblock] += 1

        for s_block, g_count in g_by_s.items():
            d_count = 1 if s_block in d_family else 0
            total = d_count + g_count
            if total != 1:
                errors.append(f"(j,S) constraint for j={j}, S={s_block} has count {total}, expected 1")

    for u_block in iter_comb_tuples(v, t + 2):
        g_count = sum(1 for family in g_families if u_block in family)
        d_count = sum(1 for s_block in _subblocks(u_block, t + 1) if s_block in d_family)
        total = g_count + d_count
        if total != 1:
            errors.append(f"U-shadow constraint for U={u_block} has count {total}, expected 1")

    return errors
