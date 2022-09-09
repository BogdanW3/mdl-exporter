from ...classes.War3AnimationCurve import War3AnimationCurve
from ... import constants


def parse_material_texture_id(r) -> War3AnimationCurve:
    texture_id = War3AnimationCurve()
    tracks_count = r.getf('<I')[0]
    texture_id.interpolation = constants.INTERPOLATION_TYPE_MDL_NAMES.get(r.getf('<I')[0], 'DontInterp')
    texture_id.global_sequence = r.getf('<I')[0]

    for _ in range(tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<I')[0]    # texture id value
        texture_id.keyframes[time] = value

        if texture_id.interpolation > constants.INTERPOLATION_TYPE_LINEAR:
            in_tan = r.getf('<f')[0]
            out_tan = r.getf('<f')[0]
            texture_id.handles_left[time] = in_tan
            texture_id.handles_right[time] = out_tan
    return texture_id
