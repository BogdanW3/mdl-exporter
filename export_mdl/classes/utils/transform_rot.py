from mathutils import Quaternion


def transform_rot(keyframes, matrix):
    for frame in keyframes.keys():
        axis, angle = Quaternion(keyframes[frame]).to_axis_angle()

        axis.rotate(matrix)
        quat = Quaternion(axis, angle)
        quat.normalize()

        keyframes[frame] = tuple(quat)
