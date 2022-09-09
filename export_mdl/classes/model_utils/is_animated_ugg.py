from typing import List, Tuple, Optional, Dict, Set

import bpy.types

from ..War3AnimationAction import War3AnimationAction
from ..War3AnimationCurve import War3AnimationCurve
from ..War3ExportSettings import War3ExportSettings
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from ..animation_curve_utils.split_segment import split_segment


# def is_animated_ugg(sequences: List[War3AnimationAction],
#                     global_seqs: Set[int],
#                     animation_data: bpy.types.AnimData,
#                     optimize_tolerance: float)\
#         -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
#     anim_loc = get_wc3_animation_curve(animation_data, 'location', 3, sequences, global_seqs)
#     optimize_anim(anim_loc, optimize_tolerance, sequences)
#
#     anim_rot = get_wc3_animation_curve(animation_data, 'rotation_quaternion', 4, sequences, global_seqs)
#     if anim_rot is None:
#         anim_rot = get_wc3_animation_curve(animation_data, 'rotation_euler', 3, sequences, global_seqs)
#     optimize_anim(anim_rot, optimize_tolerance, sequences)
#
#     # anim_rot_quat = get_wc3_animation_curve(animation_data, data_path % 'rotation_quaternion', 4, sequences)
#     # anim_rot_euler = get_wc3_animation_curve(animation_data, data_path % 'rotation_euler', 3, sequences)
#     # anim_rot = anim_rot_quat if anim_rot_quat is not None else anim_rot_euler
#     # register_global_sequence(global_seqs, anim_rot)
#
#     anim_scale = get_wc3_animation_curve(animation_data, 'scale', 3, sequences, global_seqs)
#     optimize_anim(anim_scale, optimize_tolerance, sequences)
#
#     return anim_loc, anim_rot, anim_scale


def is_animated_ugg(sequences: List[War3AnimationAction],
                    global_seqs: Set[int],
                    data_path: str,
                    actions: List[bpy.types.Action],
                    animation_data: bpy.types.AnimData,
                    optimize_tolerance: float)\
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    anim_loc = get_wc3_animation_curve(data_path % 'location', actions, 3, sequences, global_seqs)
    optimize_anim(anim_loc, optimize_tolerance, sequences)
    print((data_path % 'location'), anim_loc, animation_data)

    anim_rot = get_wc3_animation_curve(data_path % 'rotation_quaternion', actions, 4, sequences, global_seqs)
    if anim_rot is None:
        anim_rot = get_wc3_animation_curve(data_path % 'rotation_euler', actions, 3, sequences, global_seqs)
    optimize_anim(anim_rot, optimize_tolerance, sequences)

    # anim_rot_quat = get_wc3_animation_curve(animation_data, data_path % 'rotation_quaternion', 4, sequences)
    # anim_rot_euler = get_wc3_animation_curve(animation_data, data_path % 'rotation_euler', 3, sequences)
    # anim_rot = anim_rot_quat if anim_rot_quat is not None else anim_rot_euler
    # register_global_sequence(global_seqs, anim_rot)

    anim_scale = get_wc3_animation_curve('scale', actions, 3, sequences, global_seqs)
    optimize_anim(anim_scale, optimize_tolerance, sequences)

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


def optimize_anim(anim, tolerance: float, sequences: List[War3AnimationAction]):
    if anim is not None and 0 <= tolerance:
        optimize(anim, tolerance, sequences)


def optimize(anim_curve: War3AnimationCurve, tolerance: float, sequences: List[War3AnimationAction]):

    f2ms = 1000 / bpy.context.scene.render.fps

    if anim_curve.interpolation == 'Bezier':
        anim_curve.interpolation = 'Linear'  # This feature doesn't support bezier as of right now

    keyframes: Dict[float, List[float]] = anim_curve.keyframes
    curve_type = anim_curve.type
    print('Before: %d' % len(keyframes))

    new_keys = []
    for sequence in sequences:
        start = int(round(sequence.start / f2ms))
        end = int(round(sequence.end / f2ms))
        start_value = keyframes[start]
        start_ = (start, keyframes[start])
        end_ = (end, keyframes[end])
        end_value = keyframes[end]
        new_keys += [start_, end_]
        new_keys += split_segment(keyframes, curve_type, start, start_value, end, end_value, tolerance)

    keyframes.clear()
    keyframes.update(new_keys)
    print('After: %d' % len(keyframes))


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)
