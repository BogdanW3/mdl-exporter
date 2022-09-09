from mathutils import Vector, Matrix
from typing import Dict, List

from export_mdl.classes.War3AnimationCurve import War3AnimationCurve


def transform_vec1(anim_loc: War3AnimationCurve, matrix: Matrix):
    for frame in anim_loc.keyframes.keys():
        frame_ = anim_loc.keyframes[frame]
        vector = Vector(frame_)
        anim_loc.keyframes[frame] = list(matrix @ vector)
        if anim_loc.interpolation == 'Bezier':
            anim_loc.handles_right[frame] = list(matrix @ Vector(anim_loc.handles_right[frame]))
            anim_loc.handles_left[frame] = list(matrix @ Vector(anim_loc.handles_left[frame]))
