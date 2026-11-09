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


def _slerp(a, b, t):
    """Spherical blend that, unlike mathutils', also extrapolates (t outside 0..1)."""
    import math
    dot = sum(x * y for x, y in zip(a, b))
    if dot < 0:
        b, dot = [-c for c in b], -dot
    if dot > 0.9995:
        q = [x + (y - x) * t for x, y in zip(a, b)]
    else:
        theta = math.acos(min(1.0, dot))
        wa, wb = math.sin((1 - t) * theta) / math.sin(theta), math.sin(t * theta) / math.sin(theta)
        q = [x * wa + y * wb for x, y in zip(a, b)]
    n = math.sqrt(sum(c * c for c in q)) or 1.0
    return [c / n for c in q]


def _controls(curve, left_time, right_time):
    """The cubic Bezier control values (p0, c1, c2, p3) of the game's segment between two keys."""
    a, b = list(curve.keyframes[left_time]), list(curve.keyframes[right_time])
    out_tan, in_tan = list(curve.handles_right[left_time]), list(curve.handles_left[right_time])
    if curve.interpolation == 'Hermite':
        return a, [v + d / 3 for v, d in zip(a, out_tan)], [v - d / 3 for v, d in zip(b, in_tan)], b
    return a, out_tan, in_tan, b


def shape_sequence_bounds(fcurves, curve, frame_time: float, sequences, convert: Callable = lambda v: v):
    """Handles for the keys put at sequence bounds on a curved track (see create_transformation_curves).

    Past a sequence's last key the game follows the curve from the last key toward the first one, up to the
    sequence end: the start of that cubic, split at the end with de Casteljau, gives the last key's right handle
    and the end key's left handle. Before the first key the game does something odd (see game_value); a straight
    line from the start key to the first key stands in for it."""
    if curve is None or curve.interpolation not in ('Hermite', 'Bezier') or not curve.handles_left:
        return
    gs = curve.global_sequence
    if isinstance(gs, int) and 0 <= gs < 0x7FFFFFFF:
        return  # (Looping on a global sequence: no sequence bounds)

    def point_at(fcurve, frame):
        return next((p for p in fcurve.keyframe_points if abs(p.co[0] - frame) < 0.5), None)

    for sequence in sequences:
        start, end = sequence.start, sequence.end
        times = sorted(t for t in curve.keyframes if start <= t <= end)
        if len(times) < 2:
            continue
        first, last = times[0], times[-1]
        if last < end and last in curve.handles_right and first in curve.handles_left:
            between = first - last + (end - start)
            tau = 0.0 if between <= 0 else (end - last) / between
            p0, c1, c2, p3 = _controls(curve, last, first)
            lerp = lambda u, v: [x + (y - x) * tau for x, y in zip(u, v)]
            ab, bc, cd = lerp(p0, c1), lerp(c1, c2), lerp(c2, p3)
            q1, q2 = ab, lerp(ab, bc)
            q1, q2 = list(convert(q1)), list(convert(q2))
            f_last, f_end = round(last / frame_time), round(end / frame_time)
            third = (f_end - f_last) / 3
            for channel, fcurve in enumerate(fcurves):
                if fcurve is None or channel >= len(q1):
                    continue
                left, right = point_at(fcurve, f_last), point_at(fcurve, f_end)
                if left is None or right is None or left == right:
                    continue
                left.interpolation = 'BEZIER'
                left.handle_right_type = right.handle_left_type = 'FREE'
                left.handle_right = (f_last + third, q1[channel])
                right.handle_left = (f_end - third, q2[channel])
        if first > start:
            f_start, f_first = round(start / frame_time), round(first / frame_time)
            for fcurve in fcurves:
                if fcurve is None:
                    continue
                left, right = point_at(fcurve, f_start), point_at(fcurve, f_first)
                if left is None or right is None or left == right:
                    continue
                v0, v1 = left.co[1], right.co[1]
                left.interpolation = 'LINEAR'
                right.handle_left_type = 'FREE'
                right.handle_left = (f_first - (f_first - f_start) / 3, v1 - (v1 - v0) / 3)


def game_value(curve, now: float, start: float, end: float, quaternion: bool = False) -> Optional[list]:
    """A track's value at `now` in the sequence [start, end], evaluated the way the game does it (HiveWE,
    skeleton.ixx): past the last key it blends from the last key toward the first, before the first key it
    extrapolates that same blend (a bug the game and World Editor share), and a lone key holds. None when the
    sequence has no key (the game then shows the static value)."""
    from mathutils import Quaternion
    times = sorted(t for t in curve.keyframes if start <= t <= end)
    if not times:
        return None
    if len(times) == 1:
        return list(curve.keyframes[times[0]])
    left, right = 0, 1
    while times[right] < now:
        left, right = right, right + 1
        if right >= len(times):
            break
        if times[right] == now:
            left = right
    if times[-1] < now or times[0] > now:
        left, right = len(times) - 1, 0
    floor_time, ceil_time = times[left], times[right]
    between = ceil_time - floor_time
    if between < 0:
        between += end - start
        if now < floor_time:
            floor_time = ceil_time
    t = 0.0 if between == 0 else (now - floor_time) / between
    a, b = list(curve.keyframes[times[left]]), list(curve.keyframes[times[right]])
    kind = curve.interpolation
    if kind == 'DontInterp':
        return a
    if quaternion:
        # (Curved rotations also blend between their tangents; the plain blend is close for a held pose)
        return _slerp(a, b, t)
    out_tan, in_tan = curve.handles_right.get(times[left]), curve.handles_left.get(times[right])
    if kind in ('Hermite', 'Bezier') and out_tan and in_tan:
        t2 = t * t
        if kind == 'Hermite':
            f = (t2 * (2 * t - 3) + 1, t2 * (t - 2) + t, t2 * (t - 1), t2 * (3 - 2 * t))
        else:
            it = 1 - t
            f = (it ** 3, 3 * t * it * it, 3 * t2 * it, t2 * t)
        return [x * f[0] + y * f[1] + z * f[2] + w * f[3] for x, y, z, w in zip(a, out_tan, in_tan, b)]
    return [x + (y - x) * t for x, y in zip(a, b)]


def _squad(a, a_out, b_in, b, t):
    """The game's curved rotation between two keys (HiveWE's copy of Matrix Eater's ghostwolfSquad)."""
    return _slerp(_slerp(a, b, t), _slerp(a_out, b_in, t), 2 * t * (1 - t))


def _angle(a, b):
    import math
    dot = abs(sum(x * y for x, y in zip(a, b)))
    return math.degrees(2 * math.acos(min(1.0, dot)))


def bake_curved_rotation(curve, spans, frame_time: float, durations: List[int], max_error: float = 0.25):
    """A Hermite/Bezier rotation track as linear keys, adding keys (on whole frames) wherever a straight blend would
    stray more than `max_error` degrees from the game's curve. Blender keys quaternions per component, so it can't
    follow the game's spherical curves; this way the preview and the exported file play like the original.
    `spans` are the sequences' (start, end); a global-sequence track spans its loop. Returns a new curve."""
    import copy
    if curve is None or curve.interpolation not in ('Hermite', 'Bezier') or not curve.handles_left:
        return curve
    gs = curve.global_sequence
    if isinstance(gs, int) and 0 <= gs < len(durations):
        spans = [(0, durations[gs])]

    def wxyz(q):
        q = list(q)
        return [q[3], q[0], q[1], q[2]]  # (Tangents are read as stored, XYZW; keys were reordered to WXYZ)

    times = sorted(curve.keyframes)
    baked = copy.copy(curve)
    baked.keyframes = dict(curve.keyframes)
    baked.handles_left, baked.handles_right = {}, {}
    baked.interpolation = 'Linear'
    for t0, t1 in zip(times, times[1:]):
        if not any(s <= t0 and t1 <= e for s, e in spans):
            continue  # (The game never blends across sequences)
        if t0 not in curve.handles_right or t1 not in curve.handles_left:
            continue
        a, b = list(curve.keyframes[t0]), list(curve.keyframes[t1])
        a_out, b_in = wxyz(curve.handles_right[t0]), wxyz(curve.handles_left[t1])

        def game(time):
            return _squad(a, a_out, b_in, b, (time - t0) / (t1 - t0))

        def split(lo, hi, depth=0):
            f_lo, f_hi = round(lo / frame_time), round(hi / frame_time)
            if f_hi - f_lo < 2 or depth > 12:
                return
            mid = round((f_lo + f_hi) / 2) * frame_time
            q_lo, q_hi = baked.keyframes.get(lo) or game(lo), baked.keyframes.get(hi) or game(hi)
            worst = max(_angle(_slerp(q_lo, q_hi, (x - lo) / (hi - lo)), game(x))
                        for x in (lo + (hi - lo) * k / 4 for k in (1, 2, 3)))
            if worst <= max_error:
                return
            baked.keyframes[mid] = game(mid)
            split(lo, mid, depth + 1)
            split(mid, hi, depth + 1)
        split(t0, t1)
    return baked
