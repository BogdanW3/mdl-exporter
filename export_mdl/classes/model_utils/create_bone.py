import bpy
from mathutils import Vector
from typing import Optional

from ..War3AnimationCurve import War3AnimationCurve
from ..War3Node import War3Node


def create_bone(anim_loc: Optional[War3AnimationCurve],
                anim_rot: Optional[War3AnimationCurve],
                anim_scale: Optional[War3AnimationCurve],
                obj: bpy.types.Object,
                parent: Optional[bpy.types.Object],
                settings):
    bone = War3Node(obj.name)
    if parent is not None:
        bone.parent = parent
    else:
        bone.parent = parent

    bone.pivot = settings.global_matrix @ Vector(obj.location)
    bone.anim_loc = anim_loc
    bone.anim_rot = anim_rot
    bone.anim_scale = anim_scale
    return bone
