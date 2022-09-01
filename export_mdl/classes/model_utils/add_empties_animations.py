from typing import Tuple, Optional, List, Set

import bpy
from mathutils import Vector, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3Attachment import War3Attachment
from ..War3EventObject import War3EventObject
from ..War3ExportSettings import War3ExportSettings
from ..War3Helper import War3Helper
from ..War3Model import War3Model
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import is_animated_ugg
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence
from ..bpy_helpers.BpyEmptyNode import BpyEmptyNode
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec, transform_vec1


def create_and_add_from_empty(war3_model: War3Model,
                              billboard_lock: Tuple[bool, bool, bool],
                              billboarded: bool,
                              bpy_obj: bpy.types.Object,
                              parent_name: Optional[str],
                              settings: War3ExportSettings):
    sequences = war3_model.sequences
    global_seqs = war3_model.global_seqs
    obj_name = bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_obj.animation_data
    pivot = settings.global_matrix @ Vector(bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, settings.global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, settings.global_matrix)

    if obj_name.startswith("SND") \
            or obj_name.startswith("UBR") \
            or obj_name.startswith("FTP") \
            or obj_name.startswith("SPL"):
        eventobj = War3EventObject(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
        for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
            eventobj.track = get_wc3_animation_curve(animation_data, datapath, 1, sequences)

            if eventobj.track is not None:
                register_global_sequence(global_seqs, eventobj.track)
                break

        war3_model.event_objects.append(eventobj)

    elif obj_name.endswith(" Ref"):
        att = War3Attachment(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
        visibility = get_visibility(sequences, bpy_obj)
        att.visibility = visibility
        register_global_sequence(global_seqs, visibility)
        att.billboarded = billboarded
        att.billboard_lock = billboard_lock
        war3_model.attachments.append(att)

    elif obj_name.startswith("Bone_"):
        bone = War3Helper(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)

        bone.billboarded = billboarded
        bone.billboard_lock = billboard_lock
        war3_model.helpers.append(bone)


def create_event(sequences: List[War3AnimationAction],
                 global_seqs: Set[int],
                 bpy_obj: bpy.types.Object,
                 parent_name: Optional[str],
                 settings: War3ExportSettings):
    obj_name = bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_obj.animation_data
    pivot = settings.global_matrix @ Vector(bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, settings.global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, settings.global_matrix)

    eventobj = War3EventObject(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
    for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
        eventobj.track = get_wc3_animation_curve(animation_data, datapath, 1, sequences)

        if eventobj.track is not None:
            register_global_sequence(global_seqs, eventobj.track)
            break

    return eventobj


def create_attachment(sequences: List[War3AnimationAction],
                      global_seqs: Set[int],
                      billboard_lock: Tuple[bool, bool, bool],
                      billboarded: bool,
                      bpy_obj: bpy.types.Object,
                      parent_name: Optional[str],
                      settings: War3ExportSettings):
    obj_name = bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_obj.animation_data
    pivot = settings.global_matrix @ Vector(bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, settings.global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, settings.global_matrix)

    att = War3Attachment(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
    visibility = get_visibility(sequences, bpy_obj)
    att.visibility = visibility
    register_global_sequence(global_seqs, visibility)
    att.billboarded = billboarded
    att.billboard_lock = billboard_lock
    return att


def create_helper(sequences: List[War3AnimationAction],
                  global_seqs: Set[int],
                  billboard_lock: Tuple[bool, bool, bool],
                  billboarded: bool,
                  bpy_obj: bpy.types.Object,
                  parent_name: Optional[str],
                  settings: War3ExportSettings):
    obj_name = bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_obj.animation_data
    pivot = settings.global_matrix @ Vector(bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, settings.global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, settings.global_matrix)

    helper = War3Helper(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)

    helper.billboarded = billboarded
    helper.billboard_lock = billboard_lock
    return helper


def create_event(sequences: List[War3AnimationAction],
                 global_seqs: Set[int],
                 bpy_empty_node: BpyEmptyNode,
                 optimize_animation: bool,
                 optimize_tolerance: bool,
                 global_matrix: Matrix):
    obj_name = bpy_empty_node.bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_empty_node.bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_empty_node.bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, optimize_animation, optimize_tolerance)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_empty_node.bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_empty_node.bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, global_matrix)

    eventobj = War3EventObject(obj_name, anim_loc, anim_rot, anim_scale, bpy_empty_node.parent_name, pivot,
                               bpy_empty_node.bpy_obj.matrix_basis)
    for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
        eventobj.track = get_wc3_animation_curve(animation_data, datapath, 1, sequences)

        if eventobj.track is not None:
            register_global_sequence(global_seqs, eventobj.track)
            break

    return eventobj


def create_attachment(sequences: List[War3AnimationAction],
                      global_seqs: Set[int],
                      bpy_empty_node: BpyEmptyNode,
                      optimize_animation: bool,
                      optimize_tolerance: bool,
                      global_matrix: Matrix):
    obj_name = bpy_empty_node.bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_empty_node.bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_empty_node.bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, optimize_animation, optimize_tolerance)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_empty_node.bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_empty_node.bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, global_matrix)

    att = War3Attachment(obj_name, anim_loc, anim_rot, anim_scale, bpy_empty_node.parent_name, pivot,
                         bpy_empty_node.bpy_obj.matrix_basis)
    visibility = get_visibility(sequences, bpy_empty_node.bpy_obj)
    att.visibility = visibility
    register_global_sequence(global_seqs, visibility)
    att.billboarded = bpy_empty_node.billboarded
    att.billboard_lock = bpy_empty_node.billboard_lock
    return att


def create_helper(sequences: List[War3AnimationAction],
                  global_seqs: Set[int], bpy_empty_node: BpyEmptyNode,
                  optimize_animation: bool,
                  optimize_tolerance: bool,
                  global_matrix: Matrix):
    obj_name = bpy_empty_node.bpy_obj.name
    animation_data: bpy.types.AnimData = bpy_empty_node.bpy_obj.animation_data
    pivot = global_matrix @ Vector(bpy_empty_node.bpy_obj.location)

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, optimize_animation, optimize_tolerance)

    register_global_sequence(global_seqs, anim_scale)
    register_global_sequence(global_seqs, anim_loc)
    register_global_sequence(global_seqs, anim_rot)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_empty_node.bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_empty_node.bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, global_matrix)

    helper = War3Helper(obj_name, anim_loc, anim_rot, anim_scale, bpy_empty_node.parent_name, pivot,
                        bpy_empty_node.bpy_obj.matrix_basis)

    helper.billboarded = bpy_empty_node.billboarded
    helper.billboard_lock = bpy_empty_node.billboard_lock
    return helper

