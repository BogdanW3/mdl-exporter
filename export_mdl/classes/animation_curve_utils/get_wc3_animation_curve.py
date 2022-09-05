import math
from typing import Optional, List, Dict, Tuple, Union, Set

import bpy
from mathutils import Euler

from ..War3AnimationAction import War3AnimationAction
from ..War3AnimationCurve import War3AnimationCurve


def get_wc3_animation_curve(anim_data: Optional[bpy.types.AnimData],
                            data_path: str,
                            num_indices: int,
                            sequences: List[War3AnimationAction], global_seqs: Set[int]) \
        -> Optional[War3AnimationCurve]:
    curves = {}
    scale = 1
    if anim_data and anim_data.action:
        for index in range(num_indices):
            curve = anim_data.action.fcurves.find(data_path, index=index)
            if curve is not None:
                curves[(data_path.split('.')[-1], index)] = curve
                # For now, i'm just interested in the type, not the whole data path.
                # Hence, the split returns the name after the last dot.

    if len(curves):
        anim_curve = get_anim_curve(curves, data_path, sequences, scale)
        register_global_sequence(global_seqs, anim_curve)
        return anim_curve
    return None


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)


def get_anim_curve(fcurves: Dict[Tuple[str, int], Union[int, bpy.types.FCurve]],
                   data_path: str,
                   sequences: List[War3AnimationAction],
                   scale=1) -> War3AnimationCurve:
    f2ms = 1000 / bpy.context.scene.render.fps

    anim_type = get_type(data_path)

    interpolation = get_interpolation(fcurves, anim_type)
    global_sequence = get_global_seq(f2ms, fcurves)
    frames: Set[float] = parse_fcurve_values(f2ms, global_sequence, fcurves, sequences)

    if len(frames) <= 1:
        interpolation = 'Linear'

    frames.update(add_start_and_end_frames(global_sequence, anim_type, f2ms, sequences))

    keyframes: Dict[float, tuple] = {}
    handles_right: Dict[float, tuple] = {}
    handles_left: Dict[float, tuple] = {}
    curves: List[int, bpy.types.FCurve] = []

    for frame in frames:
        values: List[float]
        handle_left: List[float]
        handle_right: List[float]

        keys: List[Tuple[str, int]] = sorted(fcurves.keys(), key=lambda x: x[1])

        for key in keys:
            curves.append(fcurves[key])

        values, handle_left, handle_right = interpret_fcurves(interpolation, keys, data_path, fcurves, frame, scale)

        keyframes[frame] = rotation_is_quaternation(data_path, values)

        if interpolation == 'Bezier':
            handles_left[frame] = set_handle(data_path, handle_left)
            handles_right[frame] = set_handle(data_path, handle_right)

    anim_curve = War3AnimationCurve()
    anim_curve.type = anim_type
    anim_curve.interpolation = interpolation
    anim_curve.global_sequence = global_sequence
    anim_curve.curves.extend(curves)
    anim_curve.keyframes.update(keyframes)
    anim_curve.handles_left.update(handles_left)
    anim_curve.handles_right.update(handles_right)
    return anim_curve


def get_global_seq(f2ms, fcurves):
    global_seq: int = -1
    for fcurve in fcurves.values():
        for mod in [m for m in fcurve.modifiers if m.type == 'CYCLES']:
            global_seq = max(global_seq, int(fcurve.range()[1] * f2ms))
    return global_seq


def get_interpolation(fcurves, anim_type: str):
    if anim_type == 'Boolean' or anim_type == 'Event':
        return 'DontInterp'
    for fcurve in [fc for fc in fcurves.values() if len(fc.keyframe_points)]:
        if fcurve.keyframe_points[0].interpolation == 'BEZIER' and anim_type != 'Rotation':
            # Nonlinear interpolation for rotations is disabled for now
            return 'Bezier'
        elif fcurve.keyframe_points[0].interpolation == 'CONSTANT':
            return 'DontInterp'
    return 'Linear'


def parse_fcurve_values(f2ms: float, global_seq: int,
                        fcurves: Dict[Tuple[str, int], Union[int, bpy.types.FCurve]],
                        sequences: List[War3AnimationAction]):
    frames: Set[float] = set()
    for fcurve in fcurves.values():
        for keyframe in fcurve.keyframe_points:
            frame: float = keyframe.co[0] * f2ms
            for sequence in sequences:
                if (sequence.start <= frame <= sequence.end) or global_seq > 0:
                    frames.add(keyframe.co[0])
                    break
    return frames


def add_start_and_end_frames(global_seq: int,
                             anim_type: str,
                             f2ms: float,
                             sequences: List[War3AnimationAction]):
    # We want start and end keyframes for each sequence.
    # Make sure not to do this for events and global sequences, though!
    frames: Set[float] = set()
    if global_seq < 0 and anim_type in {'Rotation', 'Translation', 'Scale'}:
        for sequence in sequences:
            frames.add(round(sequence.start / f2ms))
            frames.add(round(sequence.end / f2ms))
    return frames


def interpret_fcurves(interpolation: str, keys: List[Tuple[str, int]], data_path: str,
                      fcurves: Dict[Tuple[str, int], Union[int, bpy.types.FCurve]],
                      frame: float, scale: float) -> Tuple[List[float], List[float], List[float]]:
    values: List[float] = []
    handle_left: List[float] = []
    handle_right: List[float] = []
    for key in keys:
        value = fcurves[key].evaluate(frame)
        values.append(value * scale)

        if 'color' in data_path:
            values = values[::-1]  # Colors are stored in reverse

        if 'hide_render' in data_path:
            values = [1 - v for v in values]  # Hide_Render is the opposite of visibility!

        if interpolation == 'Bezier':
            h_left = fcurves[key].evaluate(frame - 1)
            h_right = fcurves[key].evaluate(frame + 1)
            handle_left.append(h_left)
            handle_right.append(h_right)
    return values, handle_left, handle_right


def set_handle(data_path: str, handle: List[float]):
    if 'rotation' in data_path and 'quaternion' not in data_path:
        return tuple(Euler(math.radians(v) for v in handle).to_quaternion())
    else:
        return tuple(handle)


def rotation_is_quaternation(data_path: str, values: List[float]):
    if 'rotation' in data_path and 'quaternion' not in data_path:  # Warcraft 3 only uses quaternions!
        return tuple(Euler(values).to_quaternion())
    else:
        return tuple(values)


def get_type(data_path: str):
    if 'rotation' in data_path:
        return 'Rotation'
    elif 'location' in data_path:
        return 'Translation'
    elif 'scale' in data_path:
        return 'Scale'
    elif 'color' in data_path or 'default_value' in data_path:
        return 'Color'
    elif 'event' in data_path.lower():
        return 'Event'
    elif 'visibility' in data_path.lower() or 'hide_render' in data_path.lower():
        return 'Boolean'


