from mathutils import Vector, Matrix
from typing import Dict, List

from export_mdl.classes.War3AnimationCurve import War3AnimationCurve


def transform_vec(keyframes: Dict[float, tuple],
                  interpolation: str,
                  handles_right: Dict[float, tuple],
                  handles_left: Dict[float, tuple],
                  matrix: Matrix):
    print("transform_vec1 ", matrix)
    for frame in keyframes.keys():
        vector = Vector(keyframes[frame])
        print("transform_vec1 ", vector)
        keyframes[frame] = tuple(matrix @ vector)
        if interpolation == 'Bezier':
            handles_right[frame] = tuple(matrix @ Vector(handles_right[frame]))
            handles_left[frame] = tuple(matrix @ Vector(handles_left[frame]))


def transform_vec(keyframes: Dict[float, tuple],
                  interpolation: str,
                  handles_right: Dict[float, tuple],
                  handles_left: Dict[float, tuple],
                  matrix: List[float]):
    print("transform_vec2 ", matrix)
    for frame in keyframes.keys():
        frame_ = keyframes[frame]
        vector = Vector(frame_)
        print("transform_vec2 ", vector, " frame ", frame_)
        keyframes[frame] = tuple(matrix @ vector)
        if interpolation == 'Bezier':
            handles_right[frame] = tuple(matrix @ Vector(handles_right[frame]))
            handles_left[frame] = tuple(matrix @ Vector(handles_left[frame]))


def transform_vec1(anim_loc: War3AnimationCurve, matrix: List[float]):
    # print("transform_vec12 ", matrix)
    for frame in anim_loc.keyframes.keys():
        frame_ = anim_loc.keyframes[frame]
        vector = Vector(frame_)
        # print("transform_vec2 ", vector, " frame ", frame_)
        anim_loc.keyframes[frame] = tuple(matrix @ vector)
        if anim_loc.interpolation == 'Bezier':
            anim_loc.handles_right[frame] = tuple(matrix @ Vector(anim_loc.handles_right[frame]))
            anim_loc.handles_left[frame] = tuple(matrix @ Vector(anim_loc.handles_left[frame]))
