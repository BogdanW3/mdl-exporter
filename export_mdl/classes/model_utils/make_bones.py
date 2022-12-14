from typing import List, Set

import bpy
from mathutils import Matrix, Vector

from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3Bone import War3Bone
from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1
from export_mdl.classes.bpy_helpers.BpySceneObjects import BpySceneObjects
from export_mdl.classes.model_utils.is_animated_ugg import get_loc_rot_scale


def parse_armatures(bpy_scene_objects: BpySceneObjects,
                    global_matrix: Matrix,
                    optimize_tolerance: float,
                    actions: List[bpy.types.Action],
                    sequences: List[War3AnimationAction],
                    global_seqs: Set[int]) -> List[War3Bone]:
    print("parsing armature!")
    bones: List[War3Bone] = []
    for armature in bpy_scene_objects.armatures:
        animation_data: bpy.types.AnimData = armature.animation_data
        matrix_world = Matrix(armature.matrix_world)
        for pose_bone in bpy_scene_objects.bpy_nodes[armature.name]:
            # print("armature.pose_bone", pose_bone)
            bone = get_wc3_bone(animation_data, global_matrix, global_seqs, matrix_world, pose_bone, actions, sequences,
                                optimize_tolerance)
            bones.append(bone)
    return bones


def get_wc3_bone(animation_data: bpy.types.AnimData,
                 global_matrix: Matrix,
                 global_seqs: Set[int],
                 matrix_world: Matrix,
                 pose_bone: bpy.types.PoseBone,
                 actions: List[bpy.types.Action],
                 sequences: List[War3AnimationAction],
                 optimize_tolerance: float):
    data_path = 'pose.bones[\"' + pose_bone.name + '\"].%s'
    anim_loc, anim_rot, anim_scale = get_animation_data(animation_data, pose_bone, data_path, global_matrix,
                                                        global_seqs,
                                                        matrix_world, actions, sequences, optimize_tolerance)
    b_parent = pose_bone.parent
    bone_p_name = None if b_parent is None else b_parent.name
    pivot_ = matrix_world @ Vector(pose_bone.bone.head_local)  # Armature space to world space
    pivot = global_matrix @ Vector(pivot_)  # Axis conversion
    bone = War3Bone(pose_bone.name, anim_loc, anim_rot, anim_scale, bone_p_name, pivot, pose_bone.matrix_basis)
    return bone


def get_animation_data(animation_data: bpy.types.AnimData,
                       pose_bone: bpy.types.PoseBone,
                       data_path: str,
                       global_matrix: Matrix,
                       global_seqs: Set[int],
                       matrix_world: Matrix,
                       actions: List[bpy.types.Action],
                       sequences: List[War3AnimationAction],
                       optimize_tolerance: float):
    anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, data_path, actions, animation_data,
                                                       optimize_tolerance)
    #
    # anim_loc = get_wc3_animation_curve(animation_data, data_path % 'location', 3, sequences)
    # register_global_sequence(global_seqs, anim_loc)
    #
    # anim_rot = get_wc3_animation_curve(animation_data, data_path % 'rotation_quaternion', 4, sequences)
    # if anim_rot is None:
    #     anim_rot = get_wc3_animation_curve(animation_data, data_path % 'rotation_euler', 3, sequences)
    # register_global_sequence(global_seqs, anim_rot)
    #
    # # anim_rot_quat = get_wc3_animation_curve(animation_data, data_path % 'rotation_quaternion', 4, sequences)
    # # anim_rot_euler = get_wc3_animation_curve(animation_data, data_path % 'rotation_euler', 3, sequences)
    # # anim_rot = anim_rot_quat if anim_rot_quat is not None else anim_rot_euler
    # # register_global_sequence(global_seqs, anim_rot)
    #
    # anim_scale = get_wc3_animation_curve(animation_data, data_path % 'scale', 3, sequences)
    # register_global_sequence(global_seqs, anim_scale)
    #
    # if optimize_animation:
    #     optimize_anim(anim_loc, optimize_tolerance, sequences)
    #     optimize_anim(anim_rot, optimize_tolerance, sequences)
    #     optimize_anim(anim_scale, optimize_tolerance, sequences)

    if anim_loc is not None:
        m = matrix_world @ pose_bone.bone.matrix_local
        to__x_ = m.to_3x3().to_4x4()
        x_ = global_matrix @ to__x_
        transform_vec1(anim_loc, x_)
    if anim_rot is not None:
        mat_pose_ws = matrix_world @ pose_bone.bone.matrix_local
        # mat_rest_ws = matrix_world @ b.matrix
        transform_rot(anim_rot.keyframes, mat_pose_ws)
        transform_rot(anim_rot.keyframes, global_matrix)
    return anim_loc, anim_rot, anim_scale

