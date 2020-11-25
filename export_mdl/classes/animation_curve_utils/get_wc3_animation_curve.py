from ..War3AnimationCurve import War3AnimationCurve


def get_wc3_animation_curve(anim_data, data_path, num_indices, sequences, scale=1):
    curves = {}

    if anim_data and anim_data.action:
        for index in range(num_indices):
            curve = anim_data.action.fcurves.find(data_path, index=index)
            if curve is not None:
                curves[(data_path.split('.')[-1], index)] = curve
                # For now, i'm just interested in the type, not the whole data path. Hence, the split returns the name after the last dot.

    if len(curves):
        return War3AnimationCurve(curves, data_path, sequences, scale)
    return None
