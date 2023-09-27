from typing import List, Tuple, Optional, Dict, Set

import bpy.types

from ..War3AnimationAction import War3AnimationAction
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve, get_baked_curves
from ..animation_curve_utils.split_segment import split_segment


def get_loc_rot_scale(sequences: List[War3AnimationAction],
                      global_seqs: Set[int],
                      data_path: str,
                      actions: List[bpy.types.Action],
                      animation_data: bpy.types.AnimData,
                      optimize_tolerance: float)\
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    anim_loc = get_wc3_animation_curve(data_path % 'location', actions, 3, sequences, global_seqs)
    optimize_anim(anim_loc, optimize_tolerance, sequences)
    # print((data_path % 'location'), anim_loc, animation_data)

    anim_rot = get_wc3_animation_curve(data_path % 'rotation_quaternion', actions, 4, sequences, global_seqs)
    if anim_rot is None:
        anim_rot = get_wc3_animation_curve(data_path % 'rotation_euler', actions, 3, sequences, global_seqs)
    optimize_anim(anim_rot, optimize_tolerance, sequences)

    # anim_rot_quat = get_wc3_animation_curve(animation_data, data_path % 'rotation_quaternion', 4, sequences)
    # anim_rot_euler = get_wc3_animation_curve(animation_data, data_path % 'rotation_euler', 3, sequences)
    # anim_rot = anim_rot_quat if anim_rot_quat is not None else anim_rot_euler
    # register_global_sequence(global_seqs, anim_rot)

    anim_scale = get_wc3_animation_curve(data_path % 'scale', actions, 3, sequences, global_seqs)
    optimize_anim(anim_scale, optimize_tolerance, sequences)

    return anim_loc, anim_rot, anim_scale


def get_baked_loc_rot_scale(armature: bpy.types.Object,
                            actions: List[bpy.types.Action],
                            pose_bone: bpy.types.PoseBone,
                            sequences: List[War3AnimationAction],
                            optimize_tolerance: float) \
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    print("baking animation for \"" + pose_bone.name + "\"")
    temp_anim_loc, temp_anim_rot, temp_anim_scale = get_baked_curves(armature, actions, pose_bone, sequences)
    anim_loc: Optional[War3AnimationCurve] = None
    anim_rot: Optional[War3AnimationCurve] = None
    anim_scale: Optional[War3AnimationCurve] = None
    opt_tol = max(optimize_tolerance, 0)
    optimize(temp_anim_loc, opt_tol, sequences)
    f_error = 0.000001
    # print("\tremoving non-change timelines")
    for v in temp_anim_loc.keyframes.values():
        if f_error < abs(v[0]) or f_error < abs(v[1]) or f_error < abs(v[2]):
            # print("Loc: ", v, "values: ", v[0], v[1], v[2],
            #       (f_error < abs(v[0])), (f_error < abs(v[1])), (f_error < abs(v[2])))
            anim_loc = temp_anim_loc
            break

    optimize(temp_anim_rot, opt_tol, sequences)
    for v in temp_anim_rot.keyframes.values():
        if f_error < abs(v[0] - 1) or f_error < abs(v[1]) or f_error < abs(v[2]) or f_error < abs(v[3]):
            # print("Rot: ", v, "values: ", v[0], v[1], v[2], v[3],
            #       (f_error < abs(v[0] - 1)), (f_error < abs(v[1])), (f_error < abs(v[2])), (f_error < abs(v[3])))
            anim_rot = temp_anim_rot
            break
    optimize(temp_anim_scale, opt_tol, sequences)

    for v in temp_anim_scale.keyframes.values():
        if f_error < abs(v[0] - 1) or f_error < abs(v[1] - 1) or f_error < abs(v[2] - 1):
            # print("Scale: ", v, "values: ", v[0], v[1], v[2],
            #       (f_error < abs(v[0] - 1)), (f_error < abs(v[1] - 1)), (f_error < abs(v[2] - 1)))
            anim_scale = temp_anim_scale
            break

    return anim_loc, anim_rot, anim_scale


def get_visibility(sequences: List[War3AnimationAction],
                   global_seqs: Set[int],
                   actions: List[bpy.types.Action], bpy_obj: bpy.types.Object) \
        -> Optional[War3AnimationCurve]:
    animation_data = bpy_obj.animation_data
    if animation_data is not None:
        curve = get_wc3_animation_curve('hide_render', actions, 1, sequences, global_seqs)
        if curve is not None:
            return curve
    if bpy_obj.parent is not None and bpy_obj.parent_type != 'BONE':
        visibility = get_visibility(sequences, global_seqs, actions, bpy_obj.parent)
        return visibility
    return None


def optimize_anim(anim: Optional[War3AnimationCurve], tolerance: float, sequences: List[War3AnimationAction]):
    if anim is not None and 0 <= tolerance:
        optimize(anim, tolerance, sequences)


def optimize(anim_curve: War3AnimationCurve, tolerance: float, sequences: List[War3AnimationAction]):

    f2ms = 1000 / bpy.context.scene.render.fps

    if anim_curve.interpolation == 'Bezier':
        anim_curve.interpolation = 'Linear'  # This feature doesn't support bezier as of right now

    keyframes: Dict[float, List[float]] = anim_curve.keyframes
    curve_type = anim_curve.type
    # print('Before: %d' % len(keyframes))

    new_keys: Dict[float, List[float]] = {}
    for sequence in sequences:
        new_keys.update(split_segment(keyframes, curve_type, sequence.start, sequence.end, tolerance))

    keyframes.clear()
    keyframes.update(new_keys)
    # print('After: %d' % len(keyframes))

