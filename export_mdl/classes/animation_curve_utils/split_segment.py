from mathutils import Vector, Quaternion
from typing import Dict


def split_segment(keyframes: Dict[float, tuple],
                  transform_type: str,
                  start_time: int, start_value: tuple,
                  end_time: int, end_value: tuple,
                  tolerance: float):
    length = float(end_time - start_time)
    error = -1
    frame = 0
    # print('Start: %d, End: %d, Range: %f' % (start[0], end_time, length))

    for i in (i for i in range(start_time, end_time) if i in keyframes.keys()):
        distance = get_dist_from_real(end_value, i - start_time, length, keyframes[i], start_value, transform_type)

        if distance > error:
            error = distance
            frame = i

    if error > 0 and error > tolerance:
        middle = (frame, keyframes[frame])
        mid_time = frame
        mid_value = keyframes[frame]
        result = [middle]
        if frame != start_time and frame != end_time:  # Prevents infinite recursion
            result += split_segment(keyframes, transform_type, start_time, start_value, mid_time, mid_value, tolerance)
            result += split_segment(keyframes, transform_type, mid_time, mid_value, end_time, end_value, tolerance)
            return result

    return []


def get_dist_from_real(end_value: tuple,
                       time_diff: int,
                       length: float,
                       middle: tuple,
                       start_value: tuple,
                       transform_type: str):
    t = max(0.0, min(1.0, float(time_diff) / length))  # Interpolation factor
    if transform_type == 'Translation' or transform_type == 'Scale':
        a = Vector(start_value)
        b = Vector(middle)
        c = Vector(end_value)
        delta = b - a.lerp(c, t)
        return delta.magnitude  # Just the linear distance, for now
    elif transform_type == 'Rotation':
        # Spherical distance in the range of 0-2
        return 1 - Quaternion(middle).dot(Quaternion(start_value).slerp(Quaternion(end_value), t))
    return 0
