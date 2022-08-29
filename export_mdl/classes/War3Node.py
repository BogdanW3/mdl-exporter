from typing import Optional, List

from .War3AnimationCurve import War3AnimationCurve


class War3Node:  # Stores information about an MDL object (not a blender object!)
    def __init__(self, name: str,
                 anim_loc: Optional[War3AnimationCurve] = None,
                 anim_rot: Optional[War3AnimationCurve] = None,
                 anim_scale: Optional[War3AnimationCurve] = None,
                 parent: Optional[str] = None, pivot: Optional[List[float]] = None):
        # self.parent: Optional[bpy.types.Object] = parent  # bpy parent
        self.parent: Optional[str] = parent  # bpy parent
        self.name: str = name
        self.pivot: Optional[List[float]] = pivot  # TODO
        self.anim_loc: Optional[War3AnimationCurve] = anim_loc
        self.anim_rot: Optional[War3AnimationCurve] = anim_rot
        self.anim_scale: Optional[War3AnimationCurve] = anim_scale
        self.billboarded = False
        self.billboard_lock = (False, False, False)
        self.bindpose = None  # TODO

    # def set_billboard(self, billboard):
    #     bb = obj.mdl_billboard
    #     self.billboarded = bb.billboarded
    #     self.billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return hash(tuple(sorted(self.__dict__.items())))
        return hash(self.name)
