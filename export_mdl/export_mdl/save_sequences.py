from typing import TextIO, List

from ..classes.War3AnimationAction import War3AnimationAction
from ..classes.War3Model import War3Model
from ..utils import float2str, calc_bounds_radius


def save_sequences(fw: TextIO.write, model: War3Model):
    fw("Sequences %d {\n" % len(model.sequences))
    for sequence in model.sequences:
        fw("\tAnim \"%s\" {\n" % sequence.name)
        fw("\t\tInterval {%d, %d},\n" % (sequence.start, sequence.end))
        if sequence.non_looping:
            fw("\t\tNonLooping,\n")
        if sequence.rarity > 0:
            fw("\t\tRarity %d,\n" % sequence.rarity)
        if 'walk' in sequence.name.lower():
            fw("\t\tMoveSpeed %d,\n" % sequence.movement_speed)

        fw("\t\tMinimumExtent {%s, %s, %s},\n" % tuple(map(float2str, model.global_extents_min)))
        fw("\t\tMaximumExtent {%s, %s, %s},\n" % tuple(map(float2str, model.global_extents_max)))
        fw("\t\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(model.global_extents_min, model.global_extents_max)))
        fw("\t}\n")
    fw("}\n")


def save_sequences(fw: TextIO.write, sequences: List[War3AnimationAction],
                   global_extents_min: List[float],
                   global_extents_max: List[float]):
    fw("Sequences %d {\n" % len(sequences))
    for sequence in sequences:
        fw("\tAnim \"%s\" {\n" % sequence.name)
        fw("\t\tInterval {%d, %d},\n" % (sequence.start, sequence.end))
        if sequence.non_looping:
            fw("\t\tNonLooping,\n")
        if sequence.rarity > 0:
            fw("\t\tRarity %d,\n" % sequence.rarity)
        if 'walk' in sequence.name.lower():
            fw("\t\tMoveSpeed %d,\n" % sequence.movement_speed)

        fw("\t\tMinimumExtent {%s, %s, %s},\n" % tuple(map(float2str, global_extents_min)))
        fw("\t\tMaximumExtent {%s, %s, %s},\n" % tuple(map(float2str, global_extents_max)))
        fw("\t\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(global_extents_min, global_extents_max)))
        fw("\t}\n")
    fw("}\n")


def save_sequences(fw: TextIO.write, sequences: List[War3AnimationAction],
                   global_extents_min: List[float],
                   global_extents_max: List[float], f2ms: float):
    fw("Sequences %d {\n" % len(sequences))
    for sequence in sequences:
        fw("\tAnim \"%s\" {\n" % sequence.name)
        fw("\t\tInterval {%d, %d},\n" % (int(sequence.start*f2ms), int(sequence.end*f2ms)))
        if sequence.non_looping:
            fw("\t\tNonLooping,\n")
        if sequence.rarity > 0:
            fw("\t\tRarity %d,\n" % sequence.rarity)
        if 'walk' in sequence.name.lower():
            fw("\t\tMoveSpeed %d,\n" % sequence.movement_speed)

        fw("\t\tMinimumExtent {%s, %s, %s},\n" % tuple(map(float2str, global_extents_min)))
        fw("\t\tMaximumExtent {%s, %s, %s},\n" % tuple(map(float2str, global_extents_max)))
        fw("\t\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(global_extents_min, global_extents_max)))
        fw("\t}\n")
    fw("}\n")
