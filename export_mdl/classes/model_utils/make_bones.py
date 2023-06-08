from typing import List, Set, Optional, Tuple

import bpy
from mathutils import Matrix, Vector

from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3Bone import War3Bone
from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1
from export_mdl.classes.bpy_helpers.BpySceneObjects import BpySceneObjects
from export_mdl.classes.model_utils.is_animated_ugg import get_loc_rot_scale, get_baked_loc_rot_scale


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
            bone = get_wc3_bone(armature, animation_data, global_matrix, global_seqs, matrix_world, pose_bone, actions,
                                sequences, optimize_tolerance)
            bones.append(bone)
    if len(bones) == 0 and len(bpy_scene_objects.geosets) == 0:
        bones.append(War3Bone("No_Bones_Found"))
    return bones


def get_wc3_bone(armature: bpy.types.Object, animation_data: bpy.types.AnimData,
                 global_matrix: Matrix,
                 global_seqs: Set[int],
                 matrix_world: Matrix,
                 pose_bone: bpy.types.PoseBone,
                 actions: List[bpy.types.Action],
                 sequences: List[War3AnimationAction],
                 optimize_tolerance: float) -> War3Bone:
    data_path = 'pose.bones[\"' + pose_bone.name + '\"].%s'
    anim_loc, anim_rot, anim_scale = get_animation_data(armature, animation_data, pose_bone, data_path, global_matrix,
                                                        global_seqs,
                                                        matrix_world, actions, sequences, optimize_tolerance)
    b_parent = pose_bone.parent
    bone_p_name = None if b_parent is None else b_parent.name
    pivot_ = matrix_world @ Vector(pose_bone.bone.head_local)  # Armature space to world space
    pivot = global_matrix @ Vector(pivot_)  # Axis conversion
    bone = War3Bone(pose_bone.name, pivot, bone_p_name, anim_loc, anim_rot, anim_scale, pose_bone.matrix_basis)
    return bone


def get_animation_data(armature: bpy.types.Object, animation_data: bpy.types.AnimData,
                       pose_bone: bpy.types.PoseBone,
                       data_path: str,
                       global_matrix: Matrix,
                       global_seqs: Set[int],
                       matrix_world: Matrix,
                       actions: List[bpy.types.Action],
                       sequences: List[War3AnimationAction],
                       optimize_tolerance: float) \
        -> Tuple[Optional[War3AnimationCurve], Optional[War3AnimationCurve], Optional[War3AnimationCurve]]:
    if not pose_bone.is_in_ik_chain and len(pose_bone.constraints) == 0:
        anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, data_path, actions, animation_data,
                                                           optimize_tolerance)
    else:
        anim_loc, anim_rot, anim_scale = get_baked_loc_rot_scale(armature, actions, pose_bone, sequences,
                                                                 optimize_tolerance)

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

