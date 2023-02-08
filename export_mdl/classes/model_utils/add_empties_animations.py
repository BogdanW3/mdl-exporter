from typing import Tuple, Optional, List, Set

import bpy
from mathutils import Vector, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3Attachment import War3Attachment
from ..War3CollisionShape import War3CollisionShape
from ..War3EventObject import War3EventObject
from ..War3Helper import War3Helper
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import get_loc_rot_scale, get_visibility
from ..bpy_helpers.BpyEmptyNode import BpyEmptyNode
from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1
from ...utils import calc_extents


def get_event(sequences: List[War3AnimationAction],
              global_seqs: Set[int],
              actions: List[bpy.types.Action],
              bpy_empty_node: BpyEmptyNode,
              optimize_tolerance: float,
              global_matrix: Matrix):
    obj_name = bpy_empty_node.bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_empty_node.bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_empty_node.bpy_obj.location)

    matrix_world = bpy_empty_node.bpy_obj.matrix_world
    anim_loc, anim_rot, anim_scale = get_anims(animation_data, actions, global_matrix, global_seqs, matrix_world,
                                               optimize_tolerance, sequences)

    event_obj = War3EventObject(obj_name, pivot, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                                bpy_empty_node.bpy_obj.matrix_basis)
    for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
        event_obj.track = get_wc3_animation_curve(datapath, actions, 1, sequences, global_seqs)

    return event_obj


def get_attachment(sequences: List[War3AnimationAction],
                   global_seqs: Set[int],
                   actions: List[bpy.types.Action],
                   bpy_empty_node: BpyEmptyNode,
                   optimize_tolerance: float,
                   global_matrix: Matrix):
    obj_name = bpy_empty_node.bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_empty_node.bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_empty_node.bpy_obj.location)

    matrix_world = bpy_empty_node.bpy_obj.matrix_world
    anim_loc, anim_rot, anim_scale = get_anims(animation_data, actions, global_matrix, global_seqs, matrix_world,
                                               optimize_tolerance, sequences)

    att = War3Attachment(obj_name, pivot, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                         bpy_empty_node.bpy_obj.matrix_basis)
    visibility = get_visibility(sequences, global_seqs, actions, bpy_empty_node.bpy_obj)
    att.visibility = visibility
    att.billboarded = bpy_empty_node.billboarded
    att.billboard_lock = bpy_empty_node.billboard_lock
    return att


def get_helper(sequences: List[War3AnimationAction],
               global_seqs: Set[int],
               actions: List[bpy.types.Action],
               bpy_empty_node: BpyEmptyNode,
               optimize_tolerance: float,
               global_matrix: Matrix):
    obj_name = bpy_empty_node.bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_empty_node.bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_empty_node.bpy_obj.location)

    matrix_world = bpy_empty_node.bpy_obj.matrix_world
    anim_loc, anim_rot, anim_scale = get_anims(animation_data, actions, global_matrix, global_seqs, matrix_world,
                                               optimize_tolerance, sequences)

    helper = War3Helper(obj_name, pivot, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                        bpy_empty_node.bpy_obj.matrix_basis)

    helper.billboarded = bpy_empty_node.billboarded
    helper.billboard_lock = bpy_empty_node.billboard_lock
    return helper


def get_anims(animation_data: bpy.types.AnimData,
              actions: List[bpy.types.Action],
              global_matrix: Matrix,
              global_seqs: Set[int],
              matrix_world: Matrix,
              optimize_tolerance: bool,
              sequences: List[War3AnimationAction]):
    anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', actions, animation_data, optimize_tolerance)
    if anim_loc is not None:
        transform_vec1(anim_loc, matrix_world.inverted())
        transform_vec1(anim_loc, global_matrix)
    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, matrix_world.inverted())
        transform_rot(anim_rot.keyframes, global_matrix)
    return anim_loc, anim_rot, anim_scale


def get_collision(bpy_empty_node: BpyEmptyNode, global_matrix: Matrix):
    pivot = global_matrix @ Vector(bpy_empty_node.location)
    collider = War3CollisionShape(bpy_empty_node.name, pivot, bpy_empty_node.parent_name, None, None, None,
                                  bpy_empty_node.bpy_obj.matrix_basis)
    if 'Box' in bpy_empty_node.name \
            or bpy_empty_node.display_type == 'CUBE' \
            and 'Sphere' not in bpy_empty_node.name \
            and 'Cylinder' not in bpy_empty_node.name:
        collider.type = 'Box'
        corners: List[List[float]] = []
        # for corner in ((0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, 0.5, -0.5),
        #                (0.5, 0.5, 0.5),  (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5)):
        for corner in ((1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, 1, -1),
                       (1, 1, 1),  (-1, -1, 1), (1, -1, 1), (-1, 1, 1)):
            mat = global_matrix @ bpy_empty_node.bpy_obj.matrix_world
            corners.append(mat.to_quaternion() @ Vector(
                abs(x * bpy_empty_node.bpy_obj.empty_display_size * global_matrix.median_scale) * y for x, y in
                zip(bpy_empty_node.bpy_obj.scale, corner)))

        v_min, v_max = calc_extents(corners)

        collider.verts.extend([v_min, v_max])  # TODO: World space or relative to pivot??
    elif 'Sphere' in bpy_empty_node.name or bpy_empty_node.display_type == 'SPHERE':
        collider.type = 'Sphere'
        collider.verts.append(list(pivot))
        collider.radius = global_matrix.median_scale * max(
            abs(x * bpy_empty_node.bpy_obj.empty_display_size) for x in bpy_empty_node.bpy_obj.scale)
    # elif 'Cylinder' in bpy_empty_node.name:
    else:
        collider.type = 'Cylinder'
        collider.verts.append(list(pivot))
        collider.radius = global_matrix.median_scale * max(
            abs(x * bpy_empty_node.bpy_obj.empty_display_size) for x in bpy_empty_node.bpy_obj.scale)
    return collider
