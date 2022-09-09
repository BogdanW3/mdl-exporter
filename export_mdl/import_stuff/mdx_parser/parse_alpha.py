from typing import List

from .binary_reader import Reader
from ...classes.War3AnimationCurve import War3AnimationCurve
from ... import constants


def parse_alpha(r: Reader):
    alpha = War3AnimationCurve()
    tracks_count = r.getf('<I')[0]
    interpolation_int = r.getf('<I')[0]
    alpha.interpolation = constants.INTERPOLATION_TYPE_MDL_NAMES.get(interpolation_int, 'DontInterp')
    alpha.global_sequence = r.getf('<I')[0]

    for _ in range(tracks_count):
        time: int = r.getf('<I')[0]
        value: List[float] = list(r.getf('<f'))    # alpha value
        alpha.keyframes[time] = value

        if interpolation_int > constants.INTERPOLATION_TYPE_LINEAR:
            in_tan: List[float] = list(r.getf('<f'))
            out_tan: List[float] = list(r.getf('<f'))
            alpha.handles_left[time] = in_tan
            alpha.handles_right[time] = out_tan
    return alpha
