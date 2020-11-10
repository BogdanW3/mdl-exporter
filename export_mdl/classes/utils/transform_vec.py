from mathutils import Vector


def transform_vec(keyframes, interpolation, handles_right, handles_left, matrix):
    for frame in keyframes.keys():
        keyframes[frame] = tuple(matrix @ Vector(keyframes[frame]))
        if interpolation == 'Bezier':
            handles_right[frame] = tuple(matrix @ Vector(handles_right[frame]))
            handles_left[frame] = tuple(matrix @ Vector(handles_left[frame]))
