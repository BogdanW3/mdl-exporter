from mathutils import Vector

from ..War3Model import War3Model
from ..War3Object import War3Object
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import is_animated_ugg
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec


def add_bones(war3_model: War3Model, billboard_lock, billboarded, obj, parent, settings):
    visibility = get_visibility(war3_model.sequences, obj)
    anim_loc, anim_rot, anim_scale, is_animated = is_animated_ugg(war3_model, obj, settings)
    root = War3Object(obj.name)

    if parent is not None:
        root.parent = parent

    root.pivot = settings.global_matrix @ Vector(obj.location)
    root.anim_loc = anim_loc
    root.anim_scale = anim_scale
    root.anim_rot = anim_rot
    register_global_sequence(war3_model.global_seqs, root.anim_scale)

    if root.anim_loc is not None:
        register_global_sequence(war3_model.global_seqs, root.anim_loc)
        if obj.parent is not None:
            transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
                          root.anim_loc.handles_left, obj.parent.matrix_world.inverted())

        transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
                      root.anim_loc.handles_left, settings.global_matrix)

    if root.anim_rot is not None:
        register_global_sequence(war3_model.global_seqs, root.anim_rot)
        if obj.parent is not None:
            transform_rot(root.anim_rot.keyframes, obj.parent.matrix_world.inverted())

        transform_rot(root.anim_rot.keyframes, settings.global_matrix)

    root.visibility = visibility
    register_global_sequence(war3_model.global_seqs, visibility)
    root.billboarded = billboarded
    root.billboard_lock = billboard_lock
    war3_model.objects['bone'].add(root)
    for b in obj.pose.bones:
        bone = War3Object(b.name)
        if b.parent is not None:
            bone.parent = b.parent.name
        else:
            bone.parent = root.name

        bone.pivot = obj.matrix_world @ Vector(b.bone.head_local)  # Armature space to world space
        bone.pivot = settings.global_matrix @ Vector(bone.pivot)  # Axis conversion
        data_path = 'pose.bones[\"' + b.name + '\"].%s'
        bone.anim_loc = get_wc3_animation_curve(obj.animation_data, data_path % 'location', 3, war3_model.sequences)
        # get_curves(obj, data_path % 'location', (0, 1, 2))

        if settings.optimize_animation and bone.anim_loc is not None:
            bone.anim_loc.optimize(settings.optimize_tolerance, war3_model.sequences)

        bone.anim_rot = get_wc3_animation_curve(obj.animation_data, data_path % 'rotation_quaternion', 4, war3_model.sequences)
        # get_curves(obj, data_path % 'rotation_quaternion', (0, 1, 2, 3))

        if bone.anim_rot is None:
            bone.anim_rot = get_wc3_animation_curve(obj.animation_data, data_path % 'rotation_euler', 3, war3_model.sequences)

        if settings.optimize_animation and bone.anim_rot is not None:
            bone.anim_rot.optimize(settings.optimize_tolerance, war3_model.sequences)

        bone.anim_scale = get_wc3_animation_curve(obj.animation_data, data_path % 'scale', 3, war3_model.sequences)
        # get_curves(obj, data_path % 'scale', (0, 1, 2))

        if settings.optimize_animation and bone.anim_scale is not None:
            bone.anim_scale.optimize(settings.optimize_tolerance, war3_model.sequences)

        register_global_sequence(war3_model.global_seqs, bone.anim_scale)

        if bone.anim_loc is not None:
            m = obj.matrix_world @ b.bone.matrix_local
            transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                          bone.anim_loc.handles_left, settings.global_matrix @ m.to_3x3().to_4x4())
            register_global_sequence(war3_model.global_seqs, bone.anim_loc)

        if bone.anim_rot is not None:
            mat_pose_ws = obj.matrix_world @ b.bone.matrix_local
            mat_rest_ws = obj.matrix_world @ b.matrix
            transform_rot(bone.anim_rot.keyframes, mat_pose_ws)
            transform_rot(bone.anim_rot.keyframes, settings.global_matrix)
            register_global_sequence(war3_model.global_seqs, bone.anim_rot)

        war3_model.objects['bone'].add(bone)
