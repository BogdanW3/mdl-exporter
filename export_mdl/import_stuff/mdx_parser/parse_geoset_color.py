from ...classes.War3AnimationCurve import War3AnimationCurve
from ... import constants


def parse_geoset_color(r):
    color = War3AnimationCurve()
    tracks_count = r.getf('<I')[0]
    interpolation_int = r.getf('<I')[0]
    color.interpolation = constants.INTERPOLATION_TYPE_MDL_NAMES.get(interpolation_int, 'DontInterp')
    color.global_sequence = r.getf('<I')[0]

    for _ in range(tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<3f')    # color value
        color.keyframes[time] = value

        if interpolation_int > constants.INTERPOLATION_TYPE_LINEAR:
            in_tan = r.getf('<3f')
            out_tan = r.getf('<3f')
            color.handles_left[time] = in_tan
            color.handles_right[time] = out_tan

    return color
