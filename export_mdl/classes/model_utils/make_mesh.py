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
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
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
        bone: War3Bone = War3Bone(obj_name, pivot, parent_name, anim_loc, anim_rot, anim_scale,
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
                    global_seqs: Set[int])\
        -> Optional[War3GeosetAnim]:
    geo_color_anim = get_wc3_animation_curve(bpy_geoset.get_geo_color_path(), actions, 3, sequences, global_seqs)
    # for index in range(3):
    #     curve = action.fcurves.find(data_path)
    print("geo_color_anim:", geo_color_anim)
    geo_color = [1.0, 1.0, 1.0]
    if bpy_geoset.bpy_material:
        color_node = bpy_geoset.bpy_material.node_tree.nodes.get("Geoset Anim Color")
        if color_node:
            print("color_node:", color_node)
            geo_color = color_node.outputs[0].default_value
            # node_tree.nodes["Geoset Anim Color"].outputs[0].default_value
    print(geo_color)

    object_path = 'bpy.data.objects["' + bpy_geoset.name + '"]'

    geo_alpha_anim = get_wc3_animation_curve(object_path + '.hide_render', actions, 1, sequences, global_seqs)
    if not geo_alpha_anim:
        geo_alpha_anim = get_wc3_animation_curve(object_path + '.hide_viewport', actions, 1, sequences, global_seqs)
    if not geo_alpha_anim:
        geo_alpha_anim = get_wc3_animation_curve(bpy_geoset.get_geo_alpha_path(), actions, 1, sequences, global_seqs)
    geo_alpha = 1.0
    if bpy_geoset.bpy_material:
        alpha_node = bpy_geoset.bpy_material.node_tree.nodes.get("Geoset Anim Alpha")
        if alpha_node:
            geo_alpha = alpha_node.inputs[1].default_value
    print(geo_alpha)

    geoset_anim: Optional[War3GeosetAnim] = None
    if geo_color_anim or geo_alpha_anim or geo_color != [1.0, 1.0, 1.0] or geo_alpha != 1.0:
        geoset_anim = War3GeosetAnim(geo_color, [geo_alpha], geo_color_anim, geo_alpha_anim)
        geoset_anim.geoset_name = bpy_geoset.name

    return geoset_anim


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
        vertex_group_index = 0 if not len(matrix) or geoset.matrices.count(matrix) else geoset.matrices.index(matrix)
        vertex = War3Vertex(bpy_geoset.pos_list[v_index],
                            bpy_geoset.normal_list[v_index],
                            bpy_geoset.uv_list[v_index], vertex_group_index,
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
    bone: War3Bone = War3Bone(obj_name, pivot, None, anim_loc, anim_rot, anim_scale,
                              bpy_geoset.bpy_obj.matrix_basis)

    if anim_loc is not None:
        transform_vec1(anim_loc, bpy_geoset.bpy_obj.matrix_world.inverted())
        transform_vec1(anim_loc, settings.global_matrix)

    if anim_rot is not None:
        transform_rot(anim_rot.keyframes, bpy_geoset.bpy_obj.matrix_world.inverted())
        transform_rot(anim_rot.keyframes, settings.global_matrix)
    return bone
