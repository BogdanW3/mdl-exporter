# import bpy
# from mathutils import Vector
# from typing import Tuple, Optional, List, Set
#
# from ..War3AnimationAction import War3AnimationAction
# from ..War3Bone import War3Bone
# from ..War3ExportSettings import War3ExportSettings
# from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
# from .is_animated_ugg import is_animated_ugg
# from .get_visibility import get_visibility
# from .register_global_sequence import register_global_sequence
# from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
# from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1
# print("add_bones!!!")
#
#
# def add_bones(sequences: List[War3AnimationAction], global_seqs: Set[int], bones: List[War3Bone],
#               billboard_lock: Tuple[bool, bool, bool],
#               billboarded: bool,
#               bpy_obj: bpy.types.Object,
#               parent_name: Optional[str],
#               settings: War3ExportSettings):
#     visibility = get_visibility(sequences, bpy_obj)
#     animation_data: bpy.types.AnimData = bpy_obj.animation_data
#     anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)
#     root_pivot = settings.global_matrix @ Vector(bpy_obj.location)
#
#     root = War3Bone(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent_name, root_pivot)
#
#     # root.pivot = settings.global_matrix @ Vector(bpy_obj.location)
#     # root.anim_loc = anim_loc
#     # root.anim_scale = anim_scale
#     # root.anim_rot = anim_rot
#     register_global_sequence(global_seqs, root.anim_scale)
#
#     if root.anim_loc is not None:
#         register_global_sequence(global_seqs, root.anim_loc)
#         if bpy_obj.parent is not None:
#             # transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
#             #               root.anim_loc.handles_left, bpy_obj.parent.matrix_world.inverted())
#             # transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
#             #               root.anim_loc.handles_left, bpy_obj.parent.matrix_parent_inverse)
#             transform_vec1(root.anim_loc, bpy_obj.parent.matrix_parent_inverse)
#
#         # transform_vec(root.anim_loc.keyframes, root.anim_loc.interpolation, root.anim_loc.handles_right,
#         #               root.anim_loc.handles_left, settings.global_matrix)
#         transform_vec1(root.anim_loc, settings.global_matrix)
#
#     if root.anim_rot is not None:
#         register_global_sequence(global_seqs, root.anim_rot)
#         if bpy_obj.parent is not None:
#             # transform_rot(root.anim_rot.keyframes, bpy_obj.parent.matrix_world.inverted())
#             transform_rot(root.anim_rot.keyframes, bpy_obj.parent.matrix_parent_inverse)
#
#         transform_rot(root.anim_rot.keyframes, settings.global_matrix)
#
#     root.visibility = visibility
#     register_global_sequence(global_seqs, visibility)
#     root.billboarded = billboarded
#     root.billboard_lock = billboard_lock
#     # war3_model.objects['bone'].append(root)
#     bones.append(root)
#     for b in bpy_obj.pose.bones:
#         # bone = War3Object(b.name)
#         data_path = 'pose.bones[\"' + b.name + '\"].%s'
#         anim_loc = get_wc3_animation_curve(bpy_obj.animation_data, data_path % 'location', 3, sequences)
#         anim_rot = get_wc3_animation_curve(bpy_obj.animation_data, data_path % 'rotation_quaternion', 4, sequences)
#         anim_scale = get_wc3_animation_curve(bpy_obj.animation_data, data_path % 'scale', 3, sequences)
#
#         b_parent = b.parent
#         bone_p_name = None if b_parent is None else b_parent.name
#
#         pivot = bpy_obj.matrix_world @ Vector(b.bone.head_local)
#         bone = War3Bone(b.name, anim_loc, anim_rot, anim_scale, bone_p_name, settings.global_matrix @ Vector(pivot))
#
#         # bone.pivot = bpy_obj.matrix_world @ Vector(b.bone.head_local)  # Armature space to world space
#         # bone.pivot = settings.global_matrix @ Vector(bone.pivot)  # Axis conversion
#         # data_path = 'pose.bones[\"' + b.name + '\"].%s'
#
#         if settings.optimize_animation and bone.anim_loc is not None:
#             bone.anim_loc.optimize(settings.optimize_tolerance, sequences)
#
#         if bone.anim_rot is None:
#             bone.anim_rot = get_wc3_animation_curve(bpy_obj.animation_data, data_path % 'rotation_euler', 3, sequences)
#
#         if settings.optimize_animation and bone.anim_rot is not None:
#             bone.anim_rot.optimize(settings.optimize_tolerance, sequences)
#
#         if settings.optimize_animation and bone.anim_scale is not None:
#             bone.anim_scale.optimize(settings.optimize_tolerance, sequences)
#
#         register_global_sequence(global_seqs, bone.anim_scale)
#
#         if bone.anim_loc is not None:
#             m = bpy_obj.matrix_world @ b.bone.matrix_local
#             to__x_ = m.to_3x3().to_4x4()
#             x_ = settings.global_matrix @ to__x_
#
#             # print(bone.name, " bone.anim_loc.keyframes ", bone.anim_loc.keyframes)
#             # transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
#             #               bone.anim_loc.handles_left, x_)
#             transform_vec1(bone.anim_loc, x_)
#             register_global_sequence(global_seqs, bone.anim_loc)
#
#         if bone.anim_rot is not None:
#             mat_pose_ws = bpy_obj.matrix_world @ b.bone.matrix_local
#             mat_rest_ws = bpy_obj.matrix_world @ b.matrix
#             transform_rot(bone.anim_rot.keyframes, mat_pose_ws)
#             transform_rot(bone.anim_rot.keyframes, settings.global_matrix)
#             register_global_sequence(global_seqs, bone.anim_rot)
#
#         # war3_model.objects['bone'].add(bone)
#         bones.append(bone)
