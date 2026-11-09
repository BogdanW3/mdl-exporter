import math
from typing import Optional, List, Dict, Tuple, Union, Set

import bpy
from mathutils import Euler, Quaternion, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3AnimationCurve import War3AnimationCurve
from ...action_compat import find_fcurve, assign_action, own_fcurve


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
            curve = find_fcurve(action, data_path, index)
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
                curve: bpy.types.FCurve = find_fcurve(action, data_path, index)
                if curve is not None:
                    curves.append(curve)

            kf_offset = seq_names_to_start.get(action.name, 0.0)
            # print(action.name, kf_offset)
            fill_anim_curve(anim_curve, curves, num_indices, data_path, kf_offset, scale)
        register_global_sequence(global_seqs, anim_curve)
        return anim_curve
    return None


def get_own_animation_curve(id_data: Optional[bpy.types.ID],
                            data_path: str,
                            num_indices: int,
                            global_seqs: Set[int],
                            sequences: Optional[List[War3AnimationAction]] = None,
                            default: Optional[List[float]] = None) -> Optional[War3AnimationCurve]:
    """A curve from the keys on this datablock's own action, on the scene timeline (the frames the sequence
    markers use).

    The game uses a track's static value in a sequence that has no keys, while Blender holds the last key. With
    sequences and the static default given, a sequence without keys whose Blender value differs from the
    default gets a key at its start, so the game shows what Blender does."""
    curves = [own_fcurve(id_data, data_path, index) for index in range(num_indices)]
    if not any(curve is not None and len(curve.keyframe_points) for curve in curves):
        return None
    if any(curve is None for curve in curves):
        return None  # Only some channels keyed; the others have no value to read here
    keyed = {(getattr(id_data, "name", ""), data_path.split('.')[-1], index): curve
             for index, curve in enumerate(curves)}
    anim_curve = get_anim_curve(keyed, data_path)
    fill_anim_curve(anim_curve, curves, num_indices, data_path, 0.0)
    if sequences and default is not None and anim_curve.global_sequence <= 0:
        for sequence in sequences:
            if any(sequence.start <= frame <= sequence.end for frame in anim_curve.keyframes):
                continue
            value = [curve.evaluate(sequence.start) for curve in curves]
            if any(abs(a - b) > 1e-6 for a, b in zip(value, default)):
                anim_curve.keyframes[sequence.start] = value
                anim_curve.handles_left[sequence.start] = value
                anim_curve.handles_right[sequence.start] = value
    register_global_sequence(global_seqs, anim_curve)
    return anim_curve


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
        assign_action(armature, action)
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

    # Colors stay RGB here; the MDL writer turns them BGR, MDX stores them RGB
    # Hiding is the opposite of visibility
    invert = data_path.endswith('hide_render') or data_path.endswith('hide_viewport')

    for frame in sorted(frames):
        values: List[float] = []
        handle_left: List[float] = []
        handle_right: List[float] = []
        for channel in range(channels):
            value = fcurves[channel].evaluate(frame)
            values.append(value * scale)

            if anim_curve.interpolation == 'Bezier':
                h_left = fcurves[channel].evaluate(frame - 1)
                h_right = fcurves[channel].evaluate(frame + 1)
                handle_left.append(h_left)
                handle_right.append(h_right)

        if invert:
            values = [1 - v for v in values]
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
    was_only_constant = False
    for fcurve in [fc for fc in fcurves.values() if len(fc.keyframe_points)]:
        if fcurve.keyframe_points[0].interpolation == 'BEZIER' and anim_type != 'Rotation':
            # Nonlinear interpolation for rotations is disabled for now
            return 'Bezier'
        elif fcurve.keyframe_points[0].interpolation == 'LINEAR':
            return 'Linear'
        elif fcurve.keyframe_points[0].interpolation == 'CONSTANT':
            # ugly fix to not use 'DontInterp' when interpolation is set to 'CONSTANT' in one or more static animations
            # only seen this so far in m3 models imported with https://github.com/SC2Mapster/m3addon/
            was_only_constant = True
    if was_only_constant:
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
    elif any(word in data_path.lower() for word in ('visibility', 'hide_render', 'hide_viewport')):
        return 'Boolean'
    elif 'alpha' in data_path.lower():
        return 'Alpha'
