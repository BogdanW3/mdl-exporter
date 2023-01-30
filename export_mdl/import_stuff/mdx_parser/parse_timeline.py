from typing import List

from .binary_reader import Reader
from ...classes.War3AnimationCurve import War3AnimationCurve
from ... import constants

# format:
# textureId: '<I'
# alpha: '<f'
# scaling, translation: '<3f'
# rotation: '<4f'


def parse_timeline(r: Reader, value_format: str) -> War3AnimationCurve:
    transformation = War3AnimationCurve()
    tracks_count = r.getf('<I')[0]
    interpolation_int = r.getf('<I')[0]
    transformation.interpolation = constants.INTERPOLATION_TYPE_MDL_NAMES.get(interpolation_int, 'DontInterp')
    transformation.global_sequence = r.getf('<I')[0]

    # print("\ttracks_count: ", tracks_count, "interpolation: ", interpolation_int, "global_sequence: ", transformation.global_sequence,)
    for _ in range(tracks_count):
        time: int = r.getf('<I')[0]
        values: List[float] = list(r.getf(value_format))    # translation values

        if value_format == '<4f':
            values = [values[3], values[0], values[1], values[2]]  # Quat [xyzw] to [wxyz]
            # print(values)

        transformation.keyframes[time] = values

        if constants.INTERPOLATION_TYPE_LINEAR < interpolation_int:
            in_tan: List[float] = list(r.getf(value_format))
            out_tan: List[float] = list(r.getf(value_format))
            transformation.handles_left[time] = in_tan
            transformation.handles_right[time] = out_tan

    return transformation
