from typing import Optional, List, Tuple


class War3Vertex:
    def __init__(self, pos: List[float], normal: List[float], uv: List[float],
                 bone_list: Optional[List[str]] = None,
                 weight_list: Optional[List[int]] = None,
                 tangent: Optional[List[float]] = None):
        self.pos: List[float] = pos
        self.normal: [float] = normal
        self.tangent: Optional[List[float]] = tangent
        self.uv: [float] = uv
        self.bone_list: Optional[List[str]] = bone_list
        self.weight_list: Optional[List[int]] = weight_list

    def set_tangent(self, tangent: List[float]):
        self.tangent = tangent

    def set_skin_bones(self, bone_list: List[str], weight_list: [int]):
        self.bone_list = bone_list
        self.weight_list = weight_list

    def set_skin_bones(self, skinBone: Tuple[List[str], List[int]]):
        self.bone_list = skinBone[0]
        self.weight_list = skinBone[1]

