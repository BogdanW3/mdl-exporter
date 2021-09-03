from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve


def get_visibility(sequences, bpy_obj):
    if bpy_obj.animation_data is not None:
        curve = get_wc3_animation_curve(bpy_obj.animation_data, 'hide_render', 1, sequences)
        if curve is not None:
            return curve
    if bpy_obj.parent is not None and bpy_obj.parent_type != 'BONE':
        return get_visibility(sequences, bpy_obj.parent)
    return None
