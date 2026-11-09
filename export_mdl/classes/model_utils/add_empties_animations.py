from typing import List, Set

import bpy
from mathutils import Vector, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3Attachment import War3Attachment
from ..War3Bone import War3Bone
from ..War3CollisionShape import War3CollisionShape
from ..War3EventObject import War3EventObject
from ..War3Helper import War3Helper
from ..War3Node import War3Node
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import get_loc_rot_scale, get_visibility
from ..bpy_helpers.BpyEmptyNode import BpyEmptyNode
from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1
from ...utils import calc_extents
from .object_node_transform import node_pivot, node_transform_curves, node_visibility
from .is_animated_ugg import optimize_anim
from ..animation_curve_utils.get_wc3_animation_curve import get_own_animation_curve


def get_object_node(sequences: List[War3AnimationAction],
                    global_seqs: Set[int],
                    actions: List[bpy.types.Action],
                    bpy_empty_node: BpyEmptyNode,
                    optimize_tolerance: float,
                    global_matrix: Matrix,
                    nodeMaker):
    bpy_obj = bpy_empty_node.bpy_obj
    if bpy_obj.children:
        for ch in bpy_obj.children:
            print(ch, ch.type)
    obj_name = bpy_empty_node.name
    pivot = node_pivot(bpy_obj, global_matrix)
    anim_loc, anim_rot, anim_scale = get_anims(bpy_obj, global_matrix, global_seqs, optimize_tolerance, sequences)

    node = nodeMaker(obj_name, pivot, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                     bpy_obj.matrix_basis)

    node.billboarded = bpy_empty_node.billboarded
    node.billboard_lock = bpy_empty_node.billboard_lock
    return node


def get_object_nod1(sequences: List[War3AnimationAction],
                    global_seqs: Set[int],
                    actions: List[bpy.types.Action],
                    bpy_empty_node: BpyEmptyNode,
                    optimize_tolerance: float,
                    global_matrix: Matrix):
    bpy_obj = bpy_empty_node.bpy_obj
    if bpy_obj.children:
        for ch in bpy_obj.children:
            print(ch, ch.type)
    obj_name = bpy_empty_node.name
    animation_data: bpy.types.AnimData = bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_obj.location)

    matrix_world = bpy_obj.matrix_world
    anim_loc, anim_rot, anim_scale = get_anims(animation_data, actions, global_matrix, global_seqs, matrix_world,
                                               optimize_tolerance, sequences)

    node = War3Node(obj_name, -1, pivot, None, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                    bpy_obj.matrix_basis)

    node.billboarded = bpy_empty_node.billboarded
    node.billboard_lock = bpy_empty_node.billboard_lock
    return node


def get_event(sequences: List[War3AnimationAction],
              global_seqs: Set[int],
              actions: List[bpy.types.Action],
              bpy_empty_node: BpyEmptyNode,
              optimize_tolerance: float,
              global_matrix: Matrix):
    bpy_obj = bpy_empty_node.bpy_obj
    obj_name = bpy_empty_node.name
    pivot = node_pivot(bpy_obj, global_matrix)
    anim_loc, anim_rot, anim_scale = get_anims(bpy_obj, global_matrix, global_seqs, optimize_tolerance, sequences)

    event_obj = War3EventObject(obj_name, -1, pivot, None, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                                bpy_obj.matrix_basis)
    event_obj.track = None
    for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
        # The event's own keys first, then the older shared-action lookup
        event_obj.track = get_own_animation_curve(bpy_obj, datapath, 1, global_seqs) \
            or get_wc3_animation_curve(datapath, actions, 1, sequences, global_seqs)
        if event_obj.track is not None:
            break

    return event_obj


def get_attachment(sequences: List[War3AnimationAction],
                   global_seqs: Set[int],
                   actions: List[bpy.types.Action],
                   bpy_empty_node: BpyEmptyNode,
                   optimize_tolerance: float,
                   global_matrix: Matrix):
    bpy_obj = bpy_empty_node.bpy_obj
    obj_name = bpy_empty_node.name
    pivot = node_pivot(bpy_obj, global_matrix)
    anim_loc, anim_rot, anim_scale = get_anims(bpy_obj, global_matrix, global_seqs, optimize_tolerance, sequences)

    att = War3Attachment(obj_name, -1, pivot, None, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                         bpy_obj.matrix_basis)
    att.visibility = node_visibility(bpy_obj, global_seqs, sequences)
    att.path = str(bpy_obj.get("mdl_attachment_path", ""))
    att.billboarded = bpy_empty_node.billboarded
    att.billboard_lock = bpy_empty_node.billboard_lock
    return att


def get_helper(sequences: List[War3AnimationAction],
               global_seqs: Set[int],
               actions: List[bpy.types.Action],
               bpy_empty_node: BpyEmptyNode,
               optimize_tolerance: float,
               global_matrix: Matrix):
    node = get_object_node(sequences, global_seqs, actions, bpy_empty_node, optimize_tolerance, global_matrix,
                           lambda n, piv, p, l, r, s, bp: War3Helper(n, -1, piv, None, p, l, r, s, bp))
    # helper = War3Helper.create_from(node)
    return node


def get_bone(sequences: List[War3AnimationAction],
             global_seqs: Set[int],
             actions: List[bpy.types.Action],
             bpy_empty_node: BpyEmptyNode,
             optimize_tolerance: float,
             global_matrix: Matrix):
    # node = get_object_node(sequences, global_seqs, actions, bpy_empty_node, optimize_tolerance, global_matrix)
    node = get_object_node(sequences, global_seqs, actions, bpy_empty_node, optimize_tolerance, global_matrix,
                           lambda n, piv, p, l, r, s, bp: War3Bone(n, -1, piv, None, p, l, r, s, bp))
    # bone = War3Bone.create_from(node)
    return node


def get_helper1(sequences: List[War3AnimationAction],
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

    helper = War3Helper(obj_name, -1, pivot, None, bpy_empty_node.parent_name, anim_loc, anim_rot, anim_scale,
                        bpy_empty_node.bpy_obj.matrix_basis)

    helper.billboarded = bpy_empty_node.billboarded
    helper.billboard_lock = bpy_empty_node.billboard_lock
    return helper


def get_anims(bpy_obj: bpy.types.Object,
              global_matrix: Matrix,
              global_seqs: Set[int],
              optimize_tolerance: float,
              sequences: List[War3AnimationAction]):
    anim_loc, anim_rot, anim_scale = node_transform_curves(bpy_obj, global_matrix, global_seqs, sequences)
    for curve in (anim_loc, anim_rot, anim_scale):
        optimize_anim(curve, optimize_tolerance, sequences)
    return anim_loc, anim_rot, anim_scale


def get_collision(bpy_empty_node: BpyEmptyNode, global_matrix: Matrix,
                  global_seqs: Set[int] = frozenset(), sequences: List[War3AnimationAction] = ()):
    bpy_obj = bpy_empty_node.bpy_obj
    pivot = node_pivot(bpy_obj, global_matrix)
    anim_loc, anim_rot, anim_scale = node_transform_curves(bpy_obj, global_matrix, set(global_seqs), sequences)
    collider = War3CollisionShape(bpy_empty_node.name, -1, pivot, None, bpy_empty_node.parent_name,
                                  anim_loc, anim_rot, anim_scale, bpy_obj.matrix_basis)
    # The importer stores the shape; otherwise it's guessed from the name and display type
    shape = bpy_obj.get("mdl_collision_shape")
    if shape is None:
        if 'Box' in bpy_empty_node.name or bpy_empty_node.display_type == 'CUBE' \
                and 'Sphere' not in bpy_empty_node.name and 'Cylinder' not in bpy_empty_node.name:
            shape = 'Box'
        elif 'Sphere' in bpy_empty_node.name or bpy_empty_node.display_type == 'SPHERE':
            shape = 'Sphere'
        else:
            shape = 'Cylinder'
    if shape == 'Box':
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
    elif shape == 'Sphere':
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

    # Imported shapes keep the file's exact vertices and radius
    stored = bpy_obj.get("mdl_collision_vertices")
    if stored is not None and len(stored) >= 3:
        to_model = global_matrix.to_3x3()
        values = list(stored)
        collider.verts = [list(to_model @ Vector(values[i:i + 3])) for i in range(0, len(values) - 2, 3)]
        if bpy_obj.get("mdl_collision_radius") is not None:
            collider.radius = float(bpy_obj["mdl_collision_radius"]) * global_matrix.median_scale
    return collider
