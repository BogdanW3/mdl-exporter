import bpy
from bpy.types import Mesh
from mathutils import Vector
from typing import List, Optional, Tuple, Set

from ..War3AnimationAction import War3AnimationAction
from ..War3Bone import War3Bone
from ..War3ExportSettings import War3ExportSettings
from ..War3Geoset import War3Geoset
from ..War3GeosetAnim import War3GeosetAnim
from ..War3Model import War3Model
from ..War3Vertex import War3Vertex
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve, get_own_animation_curve
from .is_animated_ugg import get_loc_rot_scale, get_visibility
from ..bpy_helpers.BpyGeoset import BpyGeoset
from ..bpy_helpers.BpySceneObjects import BpySceneObjects
from export_mdl.classes.animation_curve_utils.transform_rot import transform_rot
from export_mdl.classes.animation_curve_utils.transform_vec import transform_vec1


def make_mesh(war3_model: War3Model,
              bpy_scene_objects: BpySceneObjects, actions: List[bpy.types.Action],
              billboard_lock: Tuple[bool, bool, bool],
              billboarded: bool,
              bpy_geoset: BpyGeoset,
              parent_name: Optional[str],
              settings: War3ExportSettings):
    sequences = war3_model.sequences
    global_seqs = war3_model.global_seqs
    visibility = get_visibility(sequences, global_seqs, actions, bpy_geoset.bpy_obj)
    animation_data: bpy.types.AnimData = bpy_geoset.bpy_obj.animation_data

    bpy_mesh: Mesh = bpy_scene_objects.bpy_meshes[bpy_geoset.name][1]

    # Geoset Animation
    if bpy_geoset.self_as_parent:
        anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', actions, animation_data,
                                                           settings.optimize_tolerance)
        geoset_anim = get_geoset_anim(bpy_geoset, actions, sequences, global_seqs)
        pivot = settings.global_matrix @ Vector(bpy_geoset.bpy_obj.location)

        obj_name = bpy_geoset.name
        bone: War3Bone = War3Bone(obj_name, -1, pivot, None, parent_name, anim_loc, anim_rot, anim_scale,
                                  bpy_geoset.bpy_obj.matrix_basis)
        bone.billboarded = billboarded
        bone.billboard_lock = billboard_lock

        if anim_loc is not None:
            transform_vec1(anim_loc, bpy_geoset.bpy_obj.matrix_world.inverted())
            transform_vec1(anim_loc, settings.global_matrix)

        if anim_rot is not None:
            transform_rot(anim_rot.keyframes, bpy_geoset.bpy_obj.matrix_world.inverted())
            transform_rot(anim_rot.keyframes, settings.global_matrix)

        if geoset_anim is not None:
            war3_model.geoset_anim_map[bone.name] = geoset_anim
        war3_model.bones.append(bone)

    mesh_geosets = set()
    for bpy_geoset in bpy_scene_objects.geosets:
        mesh_geosets.add(create_geoset(bpy_geoset))

    # obj.to_mesh_clear()
    bpy.data.meshes.remove(bpy_mesh)


def get_geoset_anim(bpy_geoset: BpyGeoset,
                    actions: List[bpy.types.Action],
                    sequences: List[War3AnimationAction],
                    global_seqs: Set[int]) -> Optional[War3GeosetAnim]:
    """The geoset animation of a mesh object. Read from its Warcraft 3 Geoset Animation properties (Object tab)
    first, then from the older ways: keyframed render/viewport visibility, or the material's "Geoset Anim
    Alpha"/"Geoset Anim Color" nodes. Keys are read from each datablock's own action, on the scene timeline."""
    bpy_obj = bpy_geoset.bpy_obj
    node_tree = bpy_geoset.bpy_material.node_tree if bpy_geoset.bpy_material is not None else None
    nodes = node_tree.nodes if node_tree is not None else {}

    geo_props = getattr(bpy_obj, "mdl_geoset", None)
    geo_alpha = geo_props.alpha if geo_props is not None else 1.0
    geo_color = list(geo_props.color) if geo_props is not None else [1.0, 1.0, 1.0]

    geo_alpha_anim = get_own_animation_curve(bpy_obj, 'mdl_geoset.alpha', 1, global_seqs, sequences, [1.0])
    if geo_alpha_anim is None:
        geo_alpha_anim = get_own_animation_curve(bpy_obj, 'hide_render', 1, global_seqs)
    if geo_alpha_anim is None:
        geo_alpha_anim = get_own_animation_curve(bpy_obj, 'hide_viewport', 1, global_seqs)
    if geo_alpha_anim is None and nodes.get("Geoset Anim Alpha"):
        geo_alpha_anim = get_own_animation_curve(node_tree, 'nodes["Geoset Anim Alpha"].inputs[1].default_value',
                                                 1, global_seqs)
    if geo_alpha == 1.0 and nodes.get("Geoset Anim Alpha"):
        geo_alpha = nodes["Geoset Anim Alpha"].inputs[1].default_value

    geo_color_anim = get_own_animation_curve(bpy_obj, 'mdl_geoset.color', 3, global_seqs, sequences,
                                             [1.0, 1.0, 1.0])
    if geo_color_anim is None and nodes.get("Geoset Anim Color"):
        geo_color_anim = get_own_animation_curve(node_tree, 'nodes["Geoset Anim Color"].outputs[0].default_value',
                                                 3, global_seqs)
    if geo_color == [1.0, 1.0, 1.0] and nodes.get("Geoset Anim Color"):
        geo_color = list(nodes["Geoset Anim Color"].outputs[0].default_value)[:3]

    # An animated value's static is the default (what the game shows in a sequence without keys; any sequence
    # where Blender shows something else got a key above), not whatever the curve is at the current frame
    if geo_alpha_anim is not None:
        geo_alpha = 1.0
    if geo_color_anim is not None:
        geo_color = [1.0, 1.0, 1.0]
    if geo_color_anim or geo_alpha_anim or any(abs(c - 1.0) > 1e-6 for c in geo_color) or geo_alpha != 1.0:
        color = geo_color if (geo_color_anim or any(abs(c - 1.0) > 1e-6 for c in geo_color)) else None
        geoset_anim = War3GeosetAnim(color, [geo_alpha], geo_color_anim, geo_alpha_anim)
        geoset_anim.geoset_name = bpy_geoset.name
        return geoset_anim
    return None


def create_geoset(bpy_geoset: BpyGeoset) -> War3Geoset:
    geoset = War3Geoset()
    geoset.name = bpy_geoset.name
    geoset.mat_name = bpy_geoset.material_name

    for v_key, v_index in bpy_geoset.vertex_map.items():
        matrix = []
        for bone_name in bpy_geoset.bone_list[v_index]:
            matrix.append(bone_name)
        if matrix not in geoset.matrices:
            geoset.matrices.append(matrix)
        vertex = War3Vertex(bpy_geoset.pos_list[v_index],
                            bpy_geoset.normal_list[v_index],
                            bpy_geoset.uv_list[v_index],
                            bpy_geoset.bone_list[v_index],
                            bpy_geoset.weight_list[v_index],
                            bpy_geoset.tangent_list[v_index])
        geoset.vertices.append(vertex)

    for tri_bpy, tri_war3 in bpy_geoset.tri_map.items():
        geoset.triangles.append(list(tri_war3))
    return geoset


def create_geoset_bone(bpy_geoset: BpyGeoset,
                       actions: List[bpy.types.Action],
                       sequences: List[War3AnimationAction],
                       global_seqs: Set[int],
                       settings: War3ExportSettings) -> War3Bone:
    animation_data: bpy.types.AnimData = bpy_geoset.bpy_obj.animation_data

    action: List[bpy.types.Action] = []
    if animation_data:
        action.append(animation_data.action)
    anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', action,
                                                       animation_data,
                                                       settings.optimize_tolerance)
    pivot = settings.global_matrix @ Vector(bpy_geoset.bpy_obj.location)

    obj_name = bpy_geoset.name
    bone: War3Bone = War3Bone(obj_name, -1, pivot, None, None, anim_loc, anim_rot, anim_scale,
                              bpy_geoset.bpy_obj.matrix_basis)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_geoset.bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, settings.global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_geoset.bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, settings.global_matrix)
    return bone


def create_armature_bone(bpy_geoset: BpyGeoset,
                         actions: List[bpy.types.Action],
                         sequences: List[War3AnimationAction],
                         global_seqs: Set[int],
                         settings: War3ExportSettings) -> War3Bone:
    if bpy_geoset.bpy_obj.parent:
        animation_data: bpy.types.AnimData = bpy_geoset.bpy_obj.parent.animation_data

        action: List[bpy.types.Action] = []
        if animation_data:
            action.append(animation_data.action)
        anim_loc, anim_rot, anim_scale = get_loc_rot_scale(sequences, global_seqs, '%s', action,
                                                           animation_data,
                                                           settings.optimize_tolerance)
        pivot = settings.global_matrix @ Vector(bpy_geoset.bpy_obj.parent.location)

        bone: War3Bone = War3Bone(bpy_geoset.parent_name, -1, pivot, None, None, anim_loc, anim_rot, anim_scale,
                                  bpy_geoset.bpy_obj.parent.matrix_basis)
        return bone
    else:
        pivot = settings.global_matrix @ Vector(bpy_geoset.bpy_obj.location)
        bone: War3Bone = War3Bone(bpy_geoset.parent_name, -1, pivot, None, None, None, None, None,
                                  bpy_geoset.bpy_obj.matrix_basis)
        return bone
