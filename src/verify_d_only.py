from __future__ import annotations

from collections import Counter
from itertools import combinations

from src.erdos835_one_color import Block, OneColorConfig, format_block, iter_comb_tuples


def verify_d_only(config: OneColorConfig, blocks: list[Block]) -> list[str]:
    config.validate()
    counts: Counter[Block] = Counter()
    for block in blocks:
        if len(block) != config.t + 1:
            return [f"wrong block size: {format_block(block)}"]
        normalized = tuple(sorted(block))
        if len(set(normalized)) != len(normalized):
            return [f"repeated point in block: {format_block(normalized)}"]
        for subblock in combinations(normalized, config.t):
            counts[tuple(sorted(subblock))] += 1

    errors: list[str] = []
    for t_block in iter_comb_tuples(config.v, config.t):
        count = counts[t_block]
        if count != 1:
            errors.append(f"T:{format_block(t_block)} covered {count} times")
    return errors
