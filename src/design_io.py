from __future__ import annotations

from src.erdos835_one_color import Block


def parse_blocks(text: str) -> list[Block]:
    blocks: list[Block] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.replace(",", " ").split()
        block = tuple(sorted(int(part) for part in parts))
        blocks.append(block)
    return blocks


def format_blocks(blocks: list[Block]) -> str:
    return "".join(" ".join(str(point) for point in block) + "\n" for block in blocks)
