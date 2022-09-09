from typing import List

from . import binary_reader


def parse_pivot_points(data: bytes) -> List[List[float]]:
    data_size = len(data)
    r = binary_reader.Reader(data)

    if data_size % 12 != 0:
        raise Exception('bad Pivot Point data (size % 12 != 0)')

    pivot_points_count = data_size // 12

    pivot_points: List[List[float]] = []
    for _ in range(pivot_points_count):
        point: List[float] = list(r.getf('<3f'))
        pivot_points.append(point)
    return pivot_points
