from mathutils import Vector

from ..War3Object import War3Object


def create_bone(anim_loc, anim_rot, anim_scale, obj, parent, settings):
    bone = War3Object(obj.name)
    if parent is not None:
        bone.parent = parent
    else:
        bone.parent = parent

    bone.pivot = settings.global_matrix @ Vector(obj.location)
    bone.anim_loc = anim_loc
    bone.anim_rot = anim_rot
    bone.anim_scale = anim_scale
    return bone
