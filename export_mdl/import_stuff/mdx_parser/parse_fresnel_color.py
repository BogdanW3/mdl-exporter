from ...classes.War3AnimationCurve import War3AnimationCurve
from ... import constants


def parse_fresnel_color(r):
    fresnel_color = War3AnimationCurve()
    tracks_count = r.getf('<I')[0]
    interpolation_int = r.getf('<I')[0]
    fresnel_color.interpolation = constants.INTERPOLATION_TYPE_MDL_NAMES.get(interpolation_int, 'DontInterp')
    fresnel_color.global_sequence = r.getf('<I')[0]

    for _ in range(tracks_count):
        time = r.getf('<I')[0]
        value = [r.getf('<f')[0], r.getf('<f')[0], r.getf('<f')[0]]
        fresnel_color.keyframes[time] = value

        if interpolation_int > constants.INTERPOLATION_TYPE_LINEAR:
            in_tan = [r.getf('<f')[0], r.getf('<f')[0], r.getf('<f')[0]]
            out_tan = [r.getf('<f')[0], r.getf('<f')[0], r.getf('<f')[0]]
            fresnel_color.handles_left[time] = in_tan
            fresnel_color.handles_right[time] = out_tan

    return fresnel_color
