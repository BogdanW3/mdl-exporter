from mathutils import Quaternion
from typing import Dict


def transform_rot(keyframes: Dict[float, tuple], matrix):
    for frame in keyframes.keys():
        axis, angle = Quaternion(keyframes[frame]).to_axis_angle()

        axis.rotate(matrix)
        quat = Quaternion(axis, angle)
        quat.normalize()

        keyframes[frame] = tuple(quat)
