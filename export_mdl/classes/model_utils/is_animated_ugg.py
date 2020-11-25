from ..War3AnimationCurve import War3AnimationCurve
from ..War3Model import War3Model


def is_animated_ugg(war3_model: War3Model, obj, settings):
# def is_animated_ugg(war3_model, obj, settings):
    anim_loc = War3AnimationCurve.get(obj.animation_data, 'location', 3, war3_model.sequences)
    # get_curves(obj, 'location', (0, 1, 2))

    if anim_loc is not None and settings.optimize_animation:
        anim_loc.optimize(settings.optimize_tolerance, war3_model.sequences)

    anim_rot = War3AnimationCurve.get(obj.animation_data, 'rotation_quaternion', 4, war3_model.sequences)
    # get_curves(obj, 'rotation_quaternion', (0, 1, 2, 3))

    if anim_rot is None:
        anim_rot = War3AnimationCurve.get(obj.animation_data, 'rotation_euler', 3, war3_model.sequences)

    if anim_rot is not None and settings.optimize_animation:
        anim_rot.optimize(settings.optimize_tolerance, war3_model.sequences)

    anim_scale = War3AnimationCurve.get(obj.animation_data, 'scale', 3, war3_model.sequences)
    # get_curves(obj, 'scale', (0, 1, 2))

    if anim_scale is not None and settings.optimize_animation:
        anim_scale.optimize(settings.optimize_tolerance, war3_model.sequences)

    is_animated = any((anim_loc, anim_rot, anim_scale))
    return anim_loc, anim_rot, anim_scale, is_animated
