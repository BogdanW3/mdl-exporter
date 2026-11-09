# Turning Warcraft 3 tracks into keyframes on a datablock's own action, on the scene timeline (the frames the
# sequence markers sit at).
from typing import Callable, List, Optional

import bpy

from .. import constants
from ..action_compat import own_fcurve


def key_track(id_data: bpy.types.ID,
              data_path: str,
              curve,
              frame_time: float,
              sequences,
              durations: List[int],
              static,
              assign: Callable,
              convert: Callable = lambda v: v,
              group: str = "",
              interpolation: Optional[str] = None):
    """Key a parsed track onto id_data.data_path.

    assign(value) sets the property to a converted value before each key is inserted.
    In the game a sequence without keys shows the static value, while Blender would hold the previous key, so
    such sequences get a key with the static value at their start. Global-sequence tracks become looping
    (Cycles) curves instead; their length is the global sequence's."""
    if curve is None or not curve.keyframes:
        return
    gs = curve.global_sequence
    looping = isinstance(gs, int) and 0 <= gs < len(durations)
    keys = {round(time / frame_time): convert(value) for time, value in curve.keyframes.items()}
    if not looping:
        for sequence in sequences:
            if not any(sequence.start <= time <= sequence.end for time in curve.keyframes):
                keys.setdefault(round(sequence.start / frame_time), static)
    value = None
    for frame, value in sorted(keys.items()):
        assign(value)
        id_data.keyframe_insert(data_path=data_path, frame=frame, group=group)

    forced = interpolation is not None
    if interpolation is None:
        interpolation = constants.INTERPOLATION_NAME_BLEND_NAME.get(curve.interpolation, 'LINEAR')
    channels = len(value) if isinstance(value, (list, tuple)) else 1
    fcurves = [own_fcurve(id_data, data_path, index) for index in range(channels)]
    for fcurve in fcurves:
        if fcurve is not None:
            for point in fcurve.keyframe_points:
                point.interpolation = interpolation
    if not forced and not data_path.endswith('rotation_quaternion'):
        # (Rotations interpolate on the sphere in the game, their tangents don't map onto component curves)
        def as_list(v):
            converted = convert(v)
            return list(converted) if isinstance(converted, (list, tuple)) else [converted]
        apply_tangents(fcurves, curve, frame_time, as_list)
    for index in range(channels):
        fcurve = fcurves[index]
        if fcurve is None:
            continue
        if looping:
            end = round(durations[gs] / frame_time)
            if fcurve.keyframe_points[-1].co[0] < end:
                # The loop length is where the curve ends, so close it with the first value
                fcurve.keyframe_points.insert(end, fcurve.keyframe_points[0].co[1]).interpolation = interpolation
            fcurve.modifiers.new('CYCLES')


def apply_tangents(fcurves: List[Optional[bpy.types.FCurve]], curve, frame_time: float,
                   convert: Callable = lambda v: v):
    """Shape Blender's Bezier handles after the file's Hermite or Bezier tangents.

    Between keys at f0 and f1 the game's curve is the 1D cubic Bezier v0, c1, c2, v1 with c1 = out0 and c2 = in1
    (Bezier tangents), or c1 = v0 + out0/3 and c2 = v1 - in1/3 (Hermite). Handles a third of the way along the
    segment at those values give Blender the same curve."""
    if curve is None or curve.interpolation not in ('Hermite', 'Bezier') or not curve.handles_left:
        return
    hermite = curve.interpolation == 'Hermite'
    times = sorted(curve.keyframes)
    frames = [time / frame_time for time in times]
    for i, time in enumerate(times):
        if time not in curve.handles_left or time not in curve.handles_right:
            continue
        value = list(convert(list(curve.keyframes[time])))
        in_tan = list(convert(list(curve.handles_left[time])))
        out_tan = list(convert(list(curve.handles_right[time])))
        if hermite:
            # Hermite tangents are slopes, so they turn with the value but don't move with it
            in_val = [v - t / 3 for v, t in zip(value, in_tan)]
            out_val = [v + t / 3 for v, t in zip(value, out_tan)]
        else:
            in_val, out_val = in_tan, out_tan
        frame = frames[i]
        left_x = frame - ((frame - frames[i - 1]) / 3 if i > 0 else 1 / 3)
        right_x = frame + ((frames[i + 1] - frame) / 3 if i + 1 < len(frames) else 1 / 3)
        for channel, fcurve in enumerate(fcurves):
            if fcurve is None or channel >= len(value):
                continue
            point = next((p for p in fcurve.keyframe_points if abs(p.co[0] - round(frame)) < 0.5), None)
            if point is None:
                continue
            point.interpolation = 'BEZIER'
            point.handle_left_type = 'FREE'
            point.handle_right_type = 'FREE'
            point.handle_left = (left_x, in_val[channel])
            point.handle_right = (right_x, out_val[channel])


def compatible_quaternions(curve):
    """Flip quaternion keys so neighbours are on the same side; Blender interpolates the components linearly."""
    if curve is None:
        return
    previous = None
    for time in sorted(curve.keyframes):
        q = list(curve.keyframes[time])
        if previous is not None and sum(a * b for a, b in zip(q, previous)) < 0:
            q = [-c for c in q]
            curve.keyframes[time] = q
        previous = q
