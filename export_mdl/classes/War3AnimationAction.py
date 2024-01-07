from typing import TextIO, List

from ..utils import float2str, calc_bounds_radius


class War3AnimationAction:
    def __init__(self, name, start, end, non_looping=False, movement_speed=270, rarity=0):
        self.name: str = name
        self.length = end - start
        self.start: float = start
        self.end: float = end
        self.non_looping: bool = non_looping
        self.movement_speed: int = movement_speed
        self.rarity: int = rarity

    def save_sequences(self, fw: TextIO.write, global_extents_min: List[float], global_extents_max: List[float]):
        fw("\tAnim \"%s\" {\n" % self.name)
        fw("\t\tInterval { %d, %d },\n" % (self.start, self.end))
        if self.non_looping:
            fw("\t\tNonLooping,\n")
        if self.rarity > 0:
            fw("\t\tRarity %d,\n" % self.rarity)
        if 'walk' in self.name.lower():
            fw("\t\tMoveSpeed %d,\n" % self.movement_speed)

        fw("\t\tMinimumExtent { %s, %s, %s },\n" % tuple(map(float2str, global_extents_min)))
        fw("\t\tMaximumExtent { %s, %s, %s },\n" % tuple(map(float2str, global_extents_max)))
        fw("\t\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(global_extents_min, global_extents_max)))
        fw("\t}\n")
