from typing import TextIO, List

from ..classes.War3Bone import War3Bone
from ..classes.War3Model import War3Model
from ..classes.War3Node import War3Node
from ..utils import float2str


def save_pivot_points(fw: TextIO.write, objects_all: List[War3Node]):
    if len(objects_all):
        fw("PivotPoints %d {\n" % len(objects_all))
        for obj in objects_all:
            fw("\t{ %s, %s, %s },\n" % tuple(map(float2str, obj.pivot)))
        fw("}\n")
