from ..War3AnimationCurve import War3AnimationCurve


def get_visibility(sequences, obj):
    if obj.animation_data is not None:
        curve = War3AnimationCurve.get(obj.animation_data, 'hide_render', 1, sequences)
        if curve is not None:
            return curve
    if obj.parent is not None and obj.parent_type != 'BONE':
        return get_visibility(sequences, obj.parent)
    return None
