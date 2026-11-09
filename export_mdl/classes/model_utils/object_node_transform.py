# Pivot and transform tracks of an object exported as a node (attachment, event object, collision shape, light,
# helper or bone made from an empty).
#
# A node's pivot is its rest position; its tracks are translation (from the pivot), rotation and scaling around it,
# in model space. On the Blender side:
# - with a delta location (how imported nodes are set up), that is the pivot and the location keys are the
#   translation;
# - without one, the object's location at frame 0 is the pivot and location keys are taken relative to it.
# Keys come from the object's own action, on the scene timeline.
from typing import List, Optional, Set, Tuple

import bpy
from mathutils import Matrix, Quaternion, Vector

from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_own_animation_curve

NODE_TYPE_KEY = "mdl_node_type"


def node_type(bpy_obj: bpy.types.Object) -> Optional[str]:
    """ATTACHMENT, EVENT, COLLISION or LIGHT for objects the importer made (or tagged by hand), else None."""
    value = bpy_obj.get(NODE_TYPE_KEY)
    return str(value) if value else None


def _location_animated(bpy_obj: bpy.types.Object) -> bool:
    from ...action_compat import own_fcurve
    return any(own_fcurve(bpy_obj, 'location', i) is not None for i in range(3))


def _local_rest(bpy_obj: bpy.types.Object) -> Tuple[Vector, Vector]:
    """(pivot in the object's parent space, base the location keys are measured from)."""
    delta = Vector(bpy_obj.delta_location)
    if _location_animated(bpy_obj):
        base = Vector((0.0, 0.0, 0.0)) if delta.length > 1e-9 else Vector(bpy_obj.location)
    else:
        base = Vector(bpy_obj.location)
    return delta + base, base


def parent_space(bpy_obj: bpy.types.Object) -> Matrix:
    """The rest matrix the object's own location/rotation live in (parent rest @ parent inverse)."""
    parent = bpy_obj.parent
    if parent is None:
        return Matrix.Identity(4)
    if bpy_obj.parent_type == 'BONE' and parent.type == 'ARMATURE' and bpy_obj.parent_bone in parent.data.bones:
        bone = parent.data.bones[bpy_obj.parent_bone]
        rest = parent.matrix_world @ bone.matrix_local @ Matrix.Translation((0.0, bone.length, 0.0))
    else:
        rest = rest_matrix(parent)
    return rest @ bpy_obj.matrix_parent_inverse


def rest_matrix(bpy_obj: bpy.types.Object) -> Matrix:
    pivot_local, _ = _local_rest(bpy_obj)
    return parent_space(bpy_obj) @ Matrix.Translation(pivot_local)


def node_pivot(bpy_obj: bpy.types.Object, global_matrix: Matrix) -> Vector:
    return global_matrix @ rest_matrix(bpy_obj).to_translation()


def node_transform_curves(bpy_obj: bpy.types.Object,
                          global_matrix: Matrix,
                          global_seqs: Set[int],
                          sequences) -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve],
                                              Optional[War3AnimationCurve]]:
    _, base = _local_rest(bpy_obj)
    space = parent_space(bpy_obj)
    to_model = global_matrix.to_3x3() @ space.to_3x3()
    rotation_space = (global_matrix @ space).to_quaternion()

    anim_loc = get_own_animation_curve(bpy_obj, 'location', 3, global_seqs, sequences, list(base))
    if anim_loc is not None:
        for keys in (anim_loc.keyframes, anim_loc.handles_left, anim_loc.handles_right):
            for frame in keys:
                if len(keys[frame]) >= 3:  # Handles are empty unless the curve is Bezier
                    keys[frame] = list(to_model @ (Vector(keys[frame][:3]) - base))

    if bpy_obj.rotation_mode == 'QUATERNION':
        anim_rot = get_own_animation_curve(bpy_obj, 'rotation_quaternion', 4, global_seqs, sequences,
                                           [1.0, 0.0, 0.0, 0.0])
    else:
        anim_rot = get_own_animation_curve(bpy_obj, 'rotation_euler', 3, global_seqs, sequences, [0.0, 0.0, 0.0])
    if anim_rot is not None:
        anim_rot.type = 'Rotation'
        inverse = rotation_space.inverted()
        for keys in (anim_rot.keyframes, anim_rot.handles_left, anim_rot.handles_right):
            for frame in keys:
                if len(keys[frame]) >= 4:
                    keys[frame] = list(rotation_space @ Quaternion(keys[frame][:4]) @ inverse)

    anim_scale = get_own_animation_curve(bpy_obj, 'scale', 3, global_seqs, sequences, [1.0, 1.0, 1.0])
    return anim_loc, anim_rot, anim_scale


def node_visibility(bpy_obj: bpy.types.Object, global_seqs: Set[int], sequences) -> Optional[War3AnimationCurve]:
    """Keyed render visibility (or viewport visibility) of the object itself."""
    for path in ('hide_render', 'hide_viewport'):
        curve = get_own_animation_curve(bpy_obj, path, 1, global_seqs, sequences, [1.0])
        if curve is not None:
            return curve
    return None
