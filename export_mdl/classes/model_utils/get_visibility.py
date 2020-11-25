from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve


def get_visibility(sequences, obj):
    if obj.animation_data is not None:
        curve = get_wc3_animation_curve(obj.animation_data, 'hide_render', 1, sequences)
        if curve is not None:
            return curve
    if obj.parent is not None and obj.parent_type != 'BONE':
        return get_visibility(sequences, obj.parent)
    return None
