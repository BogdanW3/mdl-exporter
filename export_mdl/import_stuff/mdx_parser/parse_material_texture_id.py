from .binary_reader import Reader
from ...classes.War3AnimationCurve import War3AnimationCurve
from ... import constants


def parse_material_texture_id(r: Reader) -> War3AnimationCurve:
    texture_id = War3AnimationCurve()
    tracks_count = r.get_int()
    interpolation_flag = r.get_int()
    texture_id.interpolation = constants.INTERPOLATION_TYPE_MDL_NAMES.get(interpolation_flag, 'DontInterp')
    texture_id.global_sequence = r.get_int()

    for _ in range(tracks_count):
        time = r.get_int()
        value = r.get_ints(1)    # texture id value
        texture_id.keyframes[time] = list(value)

        if constants.INTERPOLATION_TYPE_LINEAR < interpolation_flag:
            in_tan = r.get_ints(1)
            out_tan = r.get_ints(1)
            texture_id.handles_left[time] = list(in_tan)
            texture_id.handles_right[time] = list(out_tan)
    return texture_id
