import bpy
from typing import Optional

from ...utils import get_curves


def get_parent(bpy_obj: bpy.types.Object) -> Optional[bpy.types.Object]:
    parent: bpy.types.Object = bpy_obj.parent

    if parent is None:
        return None  # Instead return object name??

    if bpy_obj.parent_type == 'BONE':  # TODO: Check if animated - otherwise, make it a helper
        # return bpy_obj.parent_bone if bpy_obj.parent_bone != "" else None
        return bpy_obj.parent if bpy_obj.parent != "" else None

    if parent.type == 'EMPTY' and parent.name.startswith("Bone_"):
        # return parent.name
        return parent

    anim_loc = get_curves(parent, 'location', (1, 2, 3))
    anim_rot = get_curves(parent, 'rotation_quaternion', (1, 2, 3, 4))
    anim_scale = get_curves(parent, 'scale', (1, 2, 3))
    animations = (anim_loc, anim_rot, anim_scale)

    if not any(animations):
        root_parent = get_parent(parent)
        if root_parent is not None:
            return root_parent

    # return parent.name
    return parent
