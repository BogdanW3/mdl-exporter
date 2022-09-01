from typing import List, Tuple, Optional, Dict

import bpy.types

from ..War3AnimationAction import War3AnimationAction
from ..War3AnimationCurve import War3AnimationCurve
from ..War3ExportSettings import War3ExportSettings
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from ..animation_curve_utils.split_segment import split_segment


def is_animated_ugg(sequences: List[War3AnimationAction],
                    animation_data: bpy.types.AnimData,
                    settings: War3ExportSettings)\
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    anim_loc = get_wc3_animation_curve(animation_data, 'location', 3, sequences)
    # get_curves(obj, 'location', (0, 1, 2))

    # get_curves(obj, 'rotation_quaternion', (0, 1, 2, 3))
    anim_rot = get_wc3_animation_curve(animation_data, 'rotation_quaternion', 4, sequences)
    if anim_rot is None:
        anim_rot = get_wc3_animation_curve(animation_data, 'rotation_euler', 3, sequences)

    anim_scale = get_wc3_animation_curve(animation_data, 'scale', 3, sequences)
    # get_curves(obj, 'scale', (0, 1, 2))

    if settings.optimize_animation:
        tolerance: float = settings.optimize_tolerance
        optimize_anim(anim_loc, tolerance, sequences)
        optimize_anim(anim_rot, tolerance, sequences)
        optimize_anim(anim_scale, tolerance, sequences)

    return anim_loc, anim_rot, anim_scale


def is_animated_ugg(sequences: List[War3AnimationAction],
                    animation_data: bpy.types.AnimData,
                    optimize_animation: bool,
                    optimize_tolerance: bool)\
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    anim_loc = get_wc3_animation_curve(animation_data, 'location', 3, sequences)
    # get_curves(obj, 'location', (0, 1, 2))

    # get_curves(obj, 'rotation_quaternion', (0, 1, 2, 3))
    anim_rot = get_wc3_animation_curve(animation_data, 'rotation_quaternion', 4, sequences)
    if anim_rot is None:
        anim_rot = get_wc3_animation_curve(animation_data, 'rotation_euler', 3, sequences)

    anim_scale = get_wc3_animation_curve(animation_data, 'scale', 3, sequences)
    # get_curves(obj, 'scale', (0, 1, 2))

    if optimize_animation:
        tolerance: float = optimize_tolerance
        optimize_anim(anim_loc, tolerance, sequences)
        optimize_anim(anim_rot, tolerance, sequences)
        optimize_anim(anim_scale, tolerance, sequences)

    return anim_loc, anim_rot, anim_scale


def optimize_anim(anim, tolerance: float, sequences: List[War3AnimationAction]):
    if anim is not None:
        anim.optimize(tolerance, sequences)


def optimize(anim_curve: War3AnimationCurve, tolerance: float, sequences: List[War3AnimationAction]):

    f2ms = 1000 / bpy.context.scene.render.fps

    if anim_curve.interpolation == 'Bezier':
        anim_curve.interpolation = 'Linear'  # This feature doesn't support bezier as of right now

    keyframes: Dict[float, tuple] = anim_curve.keyframes
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
