from typing import TextIO, Set, List, Optional

from mathutils import Matrix

from export_mdl.utils import float2str


class War3Camera:
    def __init__(self, name,
                 obj_id: int = 0,
                 pivot: List[float] = [200, 0, 100],
                 field_of_view: float = 50,
                 far_clip: float = 500, near_clip: float = 10,
                 target: List[float] = [0, 0, 80],
                 bindpose: Optional[Matrix] = None):
        self.name: str = name
        self.obj_id: int = obj_id
        self.pivot: List[float] = pivot  # TODO
        self.field_of_view: float = field_of_view
        self.far_clip: float = far_clip
        self.near_clip: float = near_clip
        self.target: List[float] = target
        # self.anim_loc: Optional[War3AnimationCurve] = anim_loc
        # self.anim_rot: Optional[War3AnimationCurve] = anim_rot
        # self.anim_scale: Optional[War3AnimationCurve] = anim_scale
        self.bindpose: Optional[Matrix] = bindpose  # TODO

    def write_camera(self, fw: TextIO.write,
                     global_seqs: Set[int]):
        fw("Camera \"%s\" {\n" % self.name)

        fw("\tPosition { %s, %s, %s },\n" % tuple(map(float2str, self.pivot)))
        fw("\tFieldOfView %f,\n" % self.field_of_view)
        fw("\tFarClip %f,\n" % self.far_clip)
        fw("\tNearClip %f,\n" % self.near_clip)

        fw("\tTarget {\n\t\tPosition { %s, %s, %s },\n" % tuple(map(float2str, self.target)))
        fw("\t}\n")
        fw("}\n")
