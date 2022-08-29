from typing import Optional, List

from mathutils import Vector

from export_mdl.alt_classes.Bone import Bone


class GeosetVertex:
    def __init__(self):
        self.pos: Vector = Vector([0, 0, 0])
        self.norm: Vector = Vector([0, 0, 1])
        self.tang: Vector = Vector([0, 0, 0, 1])
        self.uv: Vector = Vector([0, 0])
        self.matrix: Optional[int]
        # self.skin = skin
        self.bone_list: Optional[List[Bone]]
        self.weight_list: Optional[List[float]]
