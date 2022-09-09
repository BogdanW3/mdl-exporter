import math
from typing import Optional, List, Dict, Tuple, Union, Set

import bpy
from mathutils import Euler

from ..War3AnimationAction import War3AnimationAction
from ..War3AnimationCurve import War3AnimationCurve


def get_wc3_animation_curve(data_path: str,
                            actions: List[bpy.types.Action],
                            num_indices: int,
                            sequences: List[War3AnimationAction], global_seqs: Set[int]) \
        -> Optional[War3AnimationCurve]:
    scale = 1

    curves2: Dict[Tuple[str, str, int], bpy.types.FCurve] = {}
    for action in actions:
        print(action.name)
        for index in range(num_indices):
            curve = action.fcurves.find(data_path, index=index)
            if curve is not None:
                curves2[(action.name, data_path.split('.')[-1], index)] = curve
                # (NAME, TRANSFORMATION TYPE, CHANNEL), eg. ('Stand', 'location', 0[x])

    if len(curves2):
        f2ms = 1000.0 / float(bpy.context.scene.render.fps)
        seq_names_to_start: Dict[str, float] = {}
        for sequence in sequences:
            seq_names_to_start[sequence.name] = sequence.start/f2ms
        anim_curve = get_anim_curve(curves2, data_path)
        for action in actions:
            curves: List[bpy.types.FCurve] = []
            for index in range(num_indices):
                curve: bpy.types.FCurve = action.fcurves.find(data_path, index=index)
                if curve is not None:
                    curves.append(curve)

            kf_offset = seq_names_to_start.get(action.name, 0.0)
            print(action.name, kf_offset)
            fill_anim_curve(anim_curve, curves, num_indices, data_path, kf_offset, scale)
        register_global_sequence(global_seqs, anim_curve)
        return anim_curve
    return None


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)


def get_anim_curve(fcurves: Dict[Tuple[str, str, int], bpy.types.FCurve],
                   data_path: str) -> War3AnimationCurve:
    f2ms = 1000 / bpy.context.scene.render.fps

    anim_type = get_type(data_path)

    interpolation = get_interpolation(fcurves, anim_type)
    global_sequence = get_global_seq(f2ms, fcurves)

    anim_curve = War3AnimationCurve()
    anim_curve.type = anim_type
    anim_curve.interpolation = interpolation
    anim_curve.global_sequence = global_sequence
    return anim_curve


def fill_anim_curve(anim_curve: War3AnimationCurve,
                    fcurves: List[bpy.types.FCurve],
                    channels: int,
                    data_path: str,
                    keyframe_offset: float,
                    scale=1):
    # Collect all keyframe points since it is possible to animate x, y and z individually in blender
    frames: Set[float] = set()
    for fcurve in fcurves:
        for keyframe in fcurve.keyframe_points:
            frames.add(keyframe.co[0])

    keyframes: Dict[float, List[float]] = {}
    handles_right: Dict[float, List[float]] = {}
    handles_left: Dict[float, List[float]] = {}

    for frame in sorted(frames):
        values: List[float] = []
        handle_left: List[float] = []
        handle_right: List[float] = []
        for channel in range(channels):
            value = fcurves[channel].evaluate(frame)
            values.append(value * scale)

            if 'color' in data_path:
                values = values[::-1]  # Colors are stored in reverse

            if 'hide_render' in data_path:
                values = [1 - v for v in values]  # Hide_Render is the opposite of visibility!

            if anim_curve.interpolation == 'Bezier':
                h_left = fcurves[channel].evaluate(frame - 1)
                h_right = fcurves[channel].evaluate(frame + 1)
                handle_left.append(h_left)
                handle_right.append(h_right)

        keyframes[frame + keyframe_offset] = rotation_is_quaternation(data_path, values)

        if len(handle_left) == len(handle_right) == len(handle_right):
            handles_left[frame + keyframe_offset] = set_handle(data_path, handle_left)
            handles_right[frame + keyframe_offset] = set_handle(data_path, handle_right)

    anim_curve.keyframes.update(keyframes)
    anim_curve.handles_left.update(handles_left)
    anim_curve.handles_right.update(handles_right)

def get_global_seq(f2ms: float, fcurves: Dict[Tuple[str, str, int], bpy.types.FCurve]):
    global_seq: int = -1
    for fcurve in fcurves.values():
        for mod in [m for m in fcurve.modifiers if m.type == 'CYCLES']:
            global_seq = max(global_seq, int(fcurve.range()[1] * f2ms))
    return global_seq


def get_interpolation(fcurves: Dict[Tuple[str, str, int], bpy.types.FCurve],
                      anim_type: str):
    if anim_type == 'Boolean' or anim_type == 'Event':
        return 'DontInterp'
    for fcurve in [fc for fc in fcurves.values() if len(fc.keyframe_points)]:
        if fcurve.keyframe_points[0].interpolation == 'BEZIER' and anim_type != 'Rotation':
            # Nonlinear interpolation for rotations is disabled for now
            return 'Bezier'
        elif fcurve.keyframe_points[0].interpolation == 'CONSTANT':
            return 'DontInterp'
    return 'Linear'


def set_handle(data_path: str, handle: List[float]):
    if 'rotation' in data_path and 'quaternion' not in data_path:
        return list(Euler(math.radians(v) for v in handle).to_quaternion())
    else:
        return handle


def rotation_is_quaternation(data_path: str, values: List[float]):
    if 'rotation' in data_path and 'quaternion' not in data_path:  # Warcraft 3 only uses quaternions!
        return list(Euler(values).to_quaternion())
    else:
        return values


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
