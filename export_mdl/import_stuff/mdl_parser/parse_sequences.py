from typing import List

from .mdl_reader import extract_bracket_content, chunkifier
from ...classes.War3AnimationAction import War3AnimationAction


def parse_sequences(data: str) -> List[War3AnimationAction]:
    sequences_string = extract_bracket_content(data)
    sequence_chunks = chunkifier(sequences_string)

    sequences: List[War3AnimationAction] = []
    for sequence_chunk in sequence_chunks:
        name = sequence_chunk.strip().split("\"")[1]
        interval_start = 0
        interval_end = 1
        move_speed = 0
        rarity = 0
        flags = False
        sequence_info = extract_bracket_content(sequence_chunk).split(",\n")

        for info in sequence_info:
            label = info.strip().split(" ")[0]

            if label == "Interval":
                interval = extract_bracket_content(info).strip().split(",")
                interval_start = int(interval[0].strip())
                interval_end = int(interval[1].strip())

            if label == "MoveSpeed":
                move_speed = float(info.strip().replace(",", "").split(" ")[1])

            if label == "NonLooping":
                flags = True

            if label == "MinimumExtent":
                extent = extract_bracket_content(info).strip().split(",")
                minimum_extent = (float(extent[0]), float(extent[1]), float(extent[2]))

            if label == "MaximumExtent":
                extent = extract_bracket_content(info).strip().split(",")
                maximum_extent = (float(extent[0]), float(extent[1]), float(extent[2]))

            if label == "BoundsRadius":
                bounds_radius = float(info.strip().replace(",", "").split(" ")[1])

            if label == "Rarity":
                rarity = float(info.strip().replace(",", "").split(" ")[1])

        sequence = War3AnimationAction(name, interval_start, interval_end, flags, move_speed, rarity)
        sequences.append(sequence)
    return sequences
