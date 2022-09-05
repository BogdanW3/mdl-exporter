from typing import List

from .mdl_reader import extract_bracket_content, extract_float_values, chunkifier


def parse_pivot_points(data: str) -> List[List[float]]:
    pivot_points_chunks = chunkifier(extract_bracket_content(data))

    pivot_points: List[List[float]] = []
    for pivot_point in pivot_points_chunks:
        pivot_points.append(extract_float_values(pivot_point))
    return pivot_points
