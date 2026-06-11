from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


Block = tuple[int, ...]
Permutation = tuple[int, ...]

POINT_COUNT = 21
BASE_TRIPLE = (0, 1, 2)
OFF_TRIPLE_BLOCK: Block = (0, 1, 3, 5, 7)

MATCHED_PAIRS: tuple[tuple[int, int], ...] = tuple(
    (left, left + 1) for left in range(3, POINT_COUNT, 2)
)

TRIPLE_MATCHING_BLOCKS: tuple[Block, ...] = tuple(
    tuple(sorted((*BASE_TRIPLE, *pair))) for pair in MATCHED_PAIRS
)

COMMON_FORCED_BLOCKS: tuple[Block, ...] = (
    *TRIPLE_MATCHING_BLOCKS,
    OFF_TRIPLE_BLOCK,
)

TERMINAL_BRANCHES: dict[str, tuple[Block, ...]] = {
    "a_star": ((0, 1, 3, 6, 8), (0, 1, 3, 9, 11)),
    "b1": ((0, 1, 3, 6, 9), (0, 1, 3, 8, 10)),
    "b2": ((0, 1, 3, 6, 9), (0, 1, 3, 8, 11)),
}


@dataclass(frozen=True)
class OrbitAudit:
    name: str
    query: tuple[int, int, int, int]
    valid_fifth_points: tuple[int, ...]
    orbits: tuple[tuple[int, ...], ...]


def _normalize_block(points: tuple[int, ...] | list[int]) -> Block:
    return tuple(sorted(points))


def _identity_permutation() -> Permutation:
    return tuple(range(POINT_COUNT))


def _swap_points(left: int, right: int) -> Permutation:
    perm = list(_identity_permutation())
    perm[left], perm[right] = perm[right], perm[left]
    return tuple(perm)


def _swap_pairs(first: tuple[int, int], second: tuple[int, int]) -> Permutation:
    perm = list(_identity_permutation())
    a, b = first
    c, d = second
    perm[a], perm[c] = perm[c], perm[a]
    perm[b], perm[d] = perm[d], perm[b]
    return tuple(perm)


def _apply_permutation_to_block(block: Block, permutation: Permutation) -> Block:
    return _normalize_block(tuple(permutation[point] for point in block))


def _valid_fifth_points(
    query: tuple[int, int, int, int],
    forced_blocks: tuple[Block, ...],
) -> tuple[int, ...]:
    query_set = set(query)
    valid: list[int] = []
    for point in range(POINT_COUNT):
        if point in query_set:
            continue
        candidate = _normalize_block((*query, point))
        if all(len(set(candidate).intersection(block)) <= 3 for block in forced_blocks):
            valid.append(point)
    return tuple(valid)


def _generators_for_moving_pairs(moving_pairs: tuple[tuple[int, int], ...]) -> tuple[Permutation, ...]:
    generators: list[Permutation] = []
    for pair in moving_pairs:
        generators.append(_swap_points(*pair))
    for first, second in zip(moving_pairs, moving_pairs[1:]):
        generators.append(_swap_pairs(first, second))
    return tuple(generators)


def _assert_generators_preserve_case(
    query: tuple[int, int, int, int],
    forced_blocks: tuple[Block, ...],
    generators: tuple[Permutation, ...],
) -> None:
    query_block = _normalize_block(query)
    forced_set = set(forced_blocks)
    for generator in generators:
        if _apply_permutation_to_block(query_block, generator) != query_block:
            raise AssertionError("generator does not preserve query set")
        image = {_apply_permutation_to_block(block, generator) for block in forced_blocks}
        if image != forced_set:
            raise AssertionError("generator does not preserve forced block set")


def _orbits_from_generators(
    valid_points: tuple[int, ...],
    generators: tuple[Permutation, ...],
) -> tuple[tuple[int, ...], ...]:
    parent = {point: point for point in valid_points}

    def find(point: int) -> int:
        while parent[point] != point:
            parent[point] = parent[parent[point]]
            point = parent[point]
        return point

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    valid_set = set(valid_points)
    for generator in generators:
        for point in valid_points:
            image = generator[point]
            if image not in valid_set:
                raise AssertionError("generator maps a valid fifth point outside valid set")
            union(point, image)

    groups: dict[int, list[int]] = {}
    for point in valid_points:
        groups.setdefault(find(point), []).append(point)
    return tuple(sorted((tuple(sorted(group)) for group in groups.values()), key=lambda group: group[0]))


def _audit_case(
    name: str,
    query: tuple[int, int, int, int],
    forced_blocks: tuple[Block, ...],
    moving_pairs: tuple[tuple[int, int], ...],
    expected_orbits: tuple[tuple[int, ...], ...],
) -> OrbitAudit:
    generators = _generators_for_moving_pairs(moving_pairs)
    _assert_generators_preserve_case(query, forced_blocks, generators)
    valid_points = _valid_fifth_points(query, forced_blocks)
    orbits = _orbits_from_generators(valid_points, generators)
    if orbits != expected_orbits:
        raise AssertionError(f"{name} orbit mismatch: expected {expected_orbits}, got {orbits}")
    return OrbitAudit(
        name=name,
        query=query,
        valid_fifth_points=valid_points,
        orbits=orbits,
    )


def audit_terminal_branch_orbits() -> tuple[OrbitAudit, ...]:
    """Return checked residual orbit data for the three terminal branches."""

    free_pairs_after_ab = tuple((left, left + 1) for left in range(9, POINT_COUNT, 2))
    free_pairs_after_terminal = tuple((left, left + 1) for left in range(11, POINT_COUNT, 2))

    branch_a_blocks = (*COMMON_FORCED_BLOCKS, (0, 1, 3, 6, 8))
    branch_b_blocks = (*COMMON_FORCED_BLOCKS, (0, 1, 3, 6, 9))

    return (
        _audit_case(
            name="initial_ab",
            query=(0, 1, 3, 6),
            forced_blocks=COMMON_FORCED_BLOCKS,
            moving_pairs=free_pairs_after_ab,
            expected_orbits=((8,), tuple(range(9, 21))),
        ),
        _audit_case(
            name="branch_a",
            query=(0, 1, 3, 9),
            forced_blocks=branch_a_blocks,
            moving_pairs=free_pairs_after_terminal,
            expected_orbits=(tuple(range(11, 21)),),
        ),
        _audit_case(
            name="branch_b",
            query=(0, 1, 3, 8),
            forced_blocks=branch_b_blocks,
            moving_pairs=free_pairs_after_terminal,
            expected_orbits=((10,), tuple(range(11, 21))),
        ),
    )
