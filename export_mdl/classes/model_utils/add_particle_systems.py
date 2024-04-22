from typing import Optional, Set, List

import bpy
from mathutils import Vector, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3ParticleEmitter import War3ParticleEmitter
from ..War3ParticleSystem import War3ParticleSystem
from .is_animated_ugg import get_loc_rot_scale, get_visibility
from ..War3RibbonEmitter import War3RibbonEmitter
from ..bpy_helpers.BpyEmitter import BpyEmitter
from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1


def get_particle_emitter(sequences: List[War3AnimationAction],
                         global_seqs: Set[int], actions: List[bpy.types.Action],
                         bpy_emitter: BpyEmitter,
                         optimize_tolerance: float,
                         global_matrix: Matrix) -> War3ParticleEmitter:
    visibility = get_visibility(sequences, global_seqs, actions, bpy_emitter.bpy_obj)

    animation_data: bpy.types.AnimData = bpy_emitter.bpy_obj.animation_data
    anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', actions, animation_data, optimize_tolerance)

    if anim_loc is not None:
        transform_vec1(anim_loc, global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, global_matrix)

    pivot = global_matrix @ Vector(bpy_emitter.bpy_obj.location)

    particle_sys: War3ParticleEmitter = War3ParticleEmitter(bpy_emitter.bpy_obj.name, -1, pivot,
                                                            None, bpy_emitter.parent_name,
                                                            anim_loc, anim_rot, anim_scale,
                                                            bpy_emitter.bpy_obj.matrix_basis)
    particle_sys.set_from(bpy_emitter.bpy_obj, actions, sequences, global_seqs)
    particle_sys.visibility = visibility

    particle_sys.billboarded = bpy_emitter.billboarded
    particle_sys.billboard_lock = bpy_emitter.billboard_lock

    return particle_sys


def get_particle_emitter2(sequences: List[War3AnimationAction],
                          global_seqs: Set[int], actions: List[bpy.types.Action],
                          bpy_emitter: BpyEmitter,
                          optimize_tolerance: float,
                          global_matrix: Matrix,
                          global_scale: float) -> War3ParticleSystem:
    visibility = get_visibility(sequences, global_seqs, actions, bpy_emitter.bpy_obj)

    animation_data: bpy.types.AnimData = bpy_emitter.bpy_obj.animation_data
    anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', actions, animation_data,
                                                       optimize_tolerance)

    if anim_loc is not None:
        transform_vec1(anim_loc, global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, global_matrix)

    pivot = global_matrix @ Vector(bpy_emitter.bpy_obj.location)

    particle_sys: War3ParticleSystem = War3ParticleSystem(bpy_emitter.bpy_obj.name, -1, pivot,
                                                          None, bpy_emitter.parent_name,
                                                          anim_loc, anim_rot, anim_scale,
                                                          bpy_emitter.bpy_obj.matrix_basis)
    particle_sys.set_from(bpy_emitter.bpy_obj, actions, sequences, global_seqs)
    particle_sys.dimensions = Vector(map(abs, global_matrix @ bpy_emitter.bpy_obj.dimensions))
    particle_sys.visibility = visibility

    particle_sys.billboarded = bpy_emitter.billboarded
    particle_sys.billboard_lock = bpy_emitter.billboard_lock

    return particle_sys


def get_ribbon_emitter(sequences: List[War3AnimationAction],
                       global_seqs: Set[int],
                       actions: List[bpy.types.Action],
                       bpy_emitter: BpyEmitter,
                       optimize_tolerance: float,
                       global_matrix: Matrix) -> War3RibbonEmitter:
    visibility = get_visibility(sequences, global_seqs, actions, bpy_emitter.bpy_obj)

    animation_data: bpy.types.AnimData = bpy_emitter.bpy_obj.animation_data
    anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', actions, animation_data,
                                                       optimize_tolerance)

    if anim_loc is not None:
        transform_vec1(anim_loc, global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, global_matrix)

    pivot = global_matrix @ Vector(bpy_emitter.location)

    particle_sys: War3RibbonEmitter = War3RibbonEmitter(bpy_emitter.name, -1, pivot,
                                                        None, bpy_emitter.parent_name,
                                                        anim_loc, anim_rot, anim_scale,
                                                        bpy_emitter.bpy_obj.matrix_basis)
    particle_sys.set_from(bpy_emitter.bpy_obj, actions, sequences, global_seqs)
    particle_sys.dimensions = Vector(map(abs, global_matrix @ bpy_emitter.bpy_obj.dimensions))
    particle_sys.visibility = visibility

    particle_sys.billboarded = bpy_emitter.billboarded
    particle_sys.billboard_lock = bpy_emitter.billboard_lock

    return particle_sys
