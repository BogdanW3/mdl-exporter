from mathutils import Vector, Quaternion
from typing import Dict, List


def split_segment(keyframes: Dict[float, List[float]],
                  transform_type: str,
                  start_time: float,
                  end_time: float,
                  tolerance: float):
    keyList = sorted([kf for kf in keyframes.keys() if start_time <= kf <= end_time])

    if len(keyList):
        new_keyframes: Dict[float, List[float]] = {keyList[0]: keyframes[keyList[0]], keyList[-1]: keyframes[keyList[-1]]}
        time_before = keyList[0]
        for i, time in enumerate(keyList):
            if 0 < i < len(keyList)-1:
                time_after = keyList[i+1]
                error = get_dist_from_real(time, keyframes[time],
                                           time_before, keyframes[time_before],
                                           time_after, keyframes[time_after],
                                           transform_type)
                if tolerance < abs(error):
                    new_keyframes[time] = keyframes[time]
                    time_before = time
        return new_keyframes
    return {}


def get_dist_from_real(time: float, value: List[float],
                       time_bef: float, value_bef: List[float],
                       time_aft: float, value_aft: List[float],
                       transform_type: str):
    t = (time-time_bef)/(time_aft-time_bef)  # Interpolation factor
    if transform_type == 'Translation' or transform_type == 'Scale':
        a = Vector(value_bef)
        b = Vector(value)
        c = Vector(value_aft)
        delta = b - a.lerp(c, t)
        return delta.magnitude  # Just the linear distance, for now
    elif transform_type == 'Rotation':
        # Spherical distance in the range of 0-2
        return 1 - Quaternion(value).dot(Quaternion(value_bef).slerp(Quaternion(value_aft), t))
    return 0
