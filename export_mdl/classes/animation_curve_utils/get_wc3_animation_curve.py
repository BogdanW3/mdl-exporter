import math
from typing import Optional, List, Dict, Tuple, Union, Set

import bpy
from mathutils import Euler, Quaternion, Matrix

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
        # print(action.name)
        for index in range(num_indices):
            curve = action.fcurves.find(data_path, index=index)
            if curve is not None:
                curves2[(action.name, data_path.split('.')[-1], index)] = curve
                # (NAME, TRANSFORMATION TYPE, CHANNEL), eg. ('Stand', 'location', 0[x])

    if len(curves2):
        seq_names_to_start: Dict[str, float] = {}
        for sequence in sequences:
            seq_names_to_start[sequence.name] = sequence.start
        anim_curve = get_anim_curve(curves2, data_path)
        for action in actions:
            curves: List[bpy.types.FCurve] = []
            for index in range(num_indices):
                curve: bpy.types.FCurve = action.fcurves.find(data_path, index=index)
                if curve is not None:
                    curves.append(curve)

            kf_offset = seq_names_to_start.get(action.name, 0.0)
            # print(action.name, kf_offset)
            fill_anim_curve(anim_curve, curves, num_indices, data_path, kf_offset, scale)
        register_global_sequence(global_seqs, anim_curve)
        return anim_curve
    return None


def get_baked_curves(armature: bpy.types.Object,
                     actions: List[bpy.types.Action],
                     pose_bone: bpy.types.PoseBone,
                     sequences: List[War3AnimationAction]) \
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    seq_names_to_start: Dict[str, float] = {}
    for sequence in sequences:
        seq_names_to_start[sequence.name] = sequence.start
    anim_loc = get_wc3_anim_curve('Translation', -1, 'Linear')
    anim_rot = get_wc3_anim_curve('Rotation', -1, 'Linear')
    anim_scale = get_wc3_anim_curve('Scale', -1, 'Linear')
    for action in actions:
        kf_offset = seq_names_to_start.get(action.name, 0.0)
        keyframes_loc: Dict[float, List[float]] = {}
        keyframes_rot: Dict[float, List[float]] = {}
        keyframes_scale: Dict[float, List[float]] = {}
        armature.animation_data.action = action
        first_frame = action.frame_range[0]
        last_frame = action.frame_range[1]
        quat_prev: Optional[Quaternion] = None
        for i in range(int(first_frame), int(last_frame), 2):
            offset_kf = i + kf_offset
            bpy.context.scene.frame_set(i)
            bone_mat: Matrix = armature.convert_space(pose_bone=pose_bone, matrix=pose_bone.matrix,
                                                      from_space='POSE', to_space='LOCAL')
            keyframes_loc[offset_kf] = bone_mat.to_translation()
            if quat_prev is not None:
                quat = bone_mat.to_quaternion().copy()
                quat.make_compatible(quat_prev)
                keyframes_rot[offset_kf] = quat
                quat_prev = quat.copy()
            else:
                quat = bone_mat.to_quaternion().copy()
                keyframes_rot[offset_kf] = quat
                quat_prev = quat.copy()
            keyframes_scale[offset_kf] = bone_mat.to_scale()
        anim_loc.keyframes.update(keyframes_loc)
        anim_rot.keyframes.update(keyframes_rot)
        anim_scale.keyframes.update(keyframes_scale)

    bpy.context.scene.frame_set(0)
    return anim_loc, anim_rot, anim_scale


def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)


def get_anim_curve(fcurves: Dict[Tuple[str, str, int], bpy.types.FCurve],
                   data_path: str) -> War3AnimationCurve:
    f2ms = 1000 / bpy.context.scene.render.fps

    anim_type = get_type(data_path)

    interpolation = get_interpolation(fcurves, anim_type)
    global_sequence = get_global_seq(f2ms, fcurves)

    return get_wc3_anim_curve(anim_type, global_sequence, interpolation)


def get_wc3_anim_curve(anim_type: str, global_sequence, interpolation) -> War3AnimationCurve:
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
    if len(handle) and 'rotation' in data_path and 'quaternion' not in data_path:
        print(math.radians(v) for v in handle)
        print(Euler(math.radians(v) for v in handle))
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
