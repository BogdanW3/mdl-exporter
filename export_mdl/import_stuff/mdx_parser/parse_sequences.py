from typing import List

from ...classes.War3AnimationAction import War3AnimationAction
from . import binary_reader


def parse_sequences(data: bytes) -> List[War3AnimationAction]:
    r = binary_reader.Reader(data)
    data_size = len(data)

    if data_size % 132 != 0:
        raise Exception('bad sequence data (size % 132 != 0)')

    sequence_count = data_size // 132

    sequences: List[War3AnimationAction] = []
    for _ in range(sequence_count):
        name = r.gets(80)
        interval_start = r.getf('<I')[0]
        interval_end = r.getf('<I')[0]
        move_speed = r.getf('<f')[0]
        flags = r.getf('<I')[0]
        rarity = r.getf('<f')[0]
        sync_point = r.getf('<I')[0]
        bounds_radius = r.getf('<f')[0]
        minimum_extent = r.getf('<3f')
        maximum_extent = r.getf('<3f')
        print(" Parsed Sequence: ", name,
              "\tstart:", interval_start, "\tend:", interval_end,
              "\tlen:", (interval_end-interval_start))
        sequence = War3AnimationAction(name, interval_start, interval_end, False, move_speed, rarity)
        sequences.append(sequence)
    return sequences
