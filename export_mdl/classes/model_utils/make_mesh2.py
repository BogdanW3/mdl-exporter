import bpy
import numpy
from bpy.types import Modifier, Armature, ArmatureModifier, Mesh, MeshLoopTriangle, VertexGroupElement
from mathutils import Vector
from typing import List, Optional, Tuple, Set, Dict

from ..War3AnimationCurve import War3AnimationCurve
from ..War3Bone import War3Bone
from ..War3ExportSettings import War3ExportSettings
from ..War3Geoset import War3Geoset
from ..War3GeosetAnim import War3GeosetAnim
from ..War3Model import War3Model
from ..War3Node import War3Node
from ..War3Vertex import War3Vertex
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import is_animated_ugg
from .get_bpy_mesh import get_bpy_mesh
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence
from ..bpy_helpers.BpyGeoset import BpyGeoset
from ..bpy_helpers.bpy_scene_helper import BpySceneObjects
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec, transform_vec1
from ...utils import rnd


def make_mesh(war3_model: War3Model,
              bpy_scene_objects: BpySceneObjects,
              billboard_lock: Tuple[bool, bool, bool],
              billboarded: bool,
              context: bpy.context,
              mats: Set[bpy.types.Material],
              bpy_obj: bpy.types.Object,
              parent_name: Optional[str],
              settings: War3ExportSettings):
    sequences = war3_model.sequences
    global_seqs = war3_model.global_seqs
    visibility = get_visibility(sequences, bpy_obj)
    animation_data: bpy.types.AnimData = bpy_obj.animation_data

    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)
    bpy_mesh: Mesh = bpy_scene_objects.bpy_meshes[bpy_obj.name][1]

    # Geoset Animation
    geoset_anim, geoset_anim_hash = get_geoset_anim(bpy_obj, visibility, war3_model)

    pivot = settings.global_matrix @ Vector(bpy_obj.location)
    obj_name = bpy_obj.name
    if any((anim_loc, anim_rot, anim_scale)):
        bone: War3Bone = War3Bone(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
        bone.billboarded = billboarded
        bone.billboard_lock = billboard_lock

        register_global_sequence(global_seqs, anim_loc)
        register_global_sequence(global_seqs, anim_rot)

        register_global_sequence(global_seqs, anim_scale)
        if anim_loc is not None:
            transform_vec1(anim_loc, bpy_obj.matrix_world.inverted())
            transform_vec1(anim_loc, settings.global_matrix)

        if anim_rot is not None:
            transform_rot(anim_rot.keyframes, bpy_obj.matrix_world.inverted())
            transform_rot(anim_rot.keyframes, settings.global_matrix)

        if geoset_anim is not None:
            war3_model.geoset_anim_map[bone.name] = geoset_anim
        war3_model.bones.append(bone)

    mesh_geosets = set()
    for bpy_geoset in bpy_scene_objects.geosets:
        mesh_geosets.add(create_geoset(bpy_geoset, bpy_scene_objects.bone_names))

    # obj.to_mesh_clear()
    bpy.data.meshes.remove(bpy_mesh)


def make_geosets(bpy_scene_objects: BpySceneObjects):
    geosets = []
    for bpy_geoset in bpy_scene_objects.geosets:
        geosets.append(create_geoset(bpy_geoset, bpy_scene_objects.bone_names))
    return geosets


def get_arm_mod(bpy_obj: bpy.types.Object) -> Optional[ArmatureModifier]:
    for m in bpy_obj.modifiers:
        if m.type == 'ARMATURE':
            return m
    return None


def get_geoset_anim(obj: bpy.types.Object, visibility: Optional[War3AnimationCurve], war3_model: War3Model)\
        -> Tuple[Optional[War3GeosetAnim], int]:
    vertex_color_anim = get_wc3_animation_curve(obj.animation_data, 'color', 3, war3_model.sequences)
    vertex_color = None
    if any(i < 0.999 for i in obj.color[:3]):
        vertex_color = tuple(obj.color[:3])
    if not any((vertex_color, vertex_color_anim)):
        mat = obj.active_material
        if mat is not None and hasattr(mat, "node_tree") and mat.node_tree is not None:
            node = mat.node_tree.nodes.get("VertexColor")
            if node is not None:
                attr = "outputs" if node.bl_idname == 'ShaderNodeRGB' else "inputs"
                vertex_color = tuple(getattr(node, attr)[0].default_value[:3])
                if hasattr(mat.node_tree, "animation_data"):
                    vertex_color_anim = get_wc3_animation_curve(
                        mat.node_tree.animation_data, 'nodes["VertexColor"].%s[0].default_value' % attr, 3,
                        war3_model.sequences)
    geoset_anim: Optional[War3GeosetAnim] = None
    geoset_anim_hash = 0
    if any((vertex_color, vertex_color_anim, visibility)):
        geoset_anim = War3GeosetAnim(vertex_color, vertex_color_anim, visibility)
        geoset_anim_hash = hash(geoset_anim)  # The hash is a bit complex, so we precompute it
    return geoset_anim, geoset_anim_hash


def create_geoset(bpy_geoset: BpyGeoset, bone_names: List[str]) -> War3Geoset:
    geoset = War3Geoset()
    geoset.mat_name = bpy_geoset.material_name

    # geoset_anim: Optional[War3GeosetAnim] = None
    # # geoset.matrices.extend(matrices)
    #
    # if geoset_anim is not None:
    #     geoset.geoset_anim = geoset_anim
    #     geoset_anim.geoset = geoset

    for v_key, v_index in bpy_geoset.vertex_map.items():
        matrix = []
        for bone_name in bpy_geoset.bone_list[v_index]:
            if bone_name in bone_names:
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

    print(geoset.vertices)
    return geoset






# import bpy
# import numpy
# from bpy.types import Modifier, Armature, ArmatureModifier, Mesh, MeshLoopTriangle, VertexGroupElement
# from mathutils import Vector
# from typing import List, Optional, Tuple, Set, Dict
#
# from ..War3AnimationCurve import War3AnimationCurve
# from ..War3Bone import War3Bone
# from ..War3ExportSettings import War3ExportSettings
# from ..War3Geoset import War3Geoset
# from ..War3GeosetAnim import War3GeosetAnim
# from ..War3Model import War3Model
# from ..War3Node import War3Node
# from ..War3Vertex import War3Vertex
# from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
# from .is_animated_ugg import is_animated_ugg
# from .get_bpy_mesh import get_bpy_mesh
# from .get_visibility import get_visibility
# from .register_global_sequence import register_global_sequence
# from ..bpy_helpers.BpyGeoset import BpyGeoset
# from ..bpy_helpers.bpy_scene_helper import BpySceneObjects
# from ..utils.transform_rot import transform_rot
# from ..utils.transform_vec import transform_vec, transform_vec1
# from ...utils import rnd
#
#
# def make_mesh(war3_model: War3Model,
#               bpy_scene_objects: BpySceneObjects,
#               billboard_lock: Tuple[bool, bool, bool],
#               billboarded: bool,
#               context: bpy.context,
#               mats: Set[bpy.types.Material],
#               bpy_obj: bpy.types.Object,
#               parent_name: Optional[str],
#               settings: War3ExportSettings):
#     sequences = war3_model.sequences
#     global_seqs = war3_model.global_seqs
#     visibility = get_visibility(sequences, bpy_obj)
#     animation_data: bpy.types.AnimData = bpy_obj.animation_data
#
#     anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, animation_data, settings)
#     bpy_mesh: Mesh = bpy_scene_objects.bpy_meshes[bpy_obj]
#
#     # Geoset Animation
#     geoset_anim, geoset_anim_hash = get_geoset_anim(bpy_obj, visibility, war3_model)
#
#     armature_mod: Optional[ArmatureModifier] = get_arm_mod(bpy_obj)
#
#     bone_names: Set[str] = set()
#     if armature_mod is not None:
#         bpy_armature: bpy.types.Object = armature_mod.object
#         arm_data: bpy.types.Armature = bpy_armature.data
#         # bone_names = set(b.name for b in armature_mod.object.data.bones)
#         bone_names = set(b.name for b in arm_data.bones)
#
#     # Make a list of all bones to use if saving skin weights
#     temp_skin_matrices: Optional[List[List[str]]] = None
#     if settings.use_skinweights:
#         bpy_mesh.calc_tangents(bpy_mesh.uv_layers.active.name)
#         if len(bone_names):
#             bpy_armature: bpy.types.Object = armature_mod.object
#             arm_data: bpy.types.Armature = bpy_armature.data
#             temp_skin_matrices = list([b.name] for b in arm_data.bones)
#             # temp_skin_matrices = list([b.name] for b in armature_mod.object.data.bones)
#
#     pivot = settings.global_matrix @ Vector(bpy_obj.location)
#     obj_name = bpy_obj.name
#     boneName: Optional[str] = None
#     if (armature_mod is None and parent_name is None) or any((anim_loc, anim_rot, anim_scale)):
#         bone: War3Bone = War3Bone(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
#         bone.billboarded = billboarded
#         bone.billboard_lock = billboard_lock
#         boneName = bone.name
#
#         register_global_sequence(global_seqs, anim_loc)
#         register_global_sequence(global_seqs, anim_rot)
#
#         register_global_sequence(global_seqs, anim_scale)
#         if anim_loc is not None:
#             transform_vec1(anim_loc, bpy_obj.matrix_world.inverted())
#             transform_vec1(anim_loc, settings.global_matrix)
#
#         if anim_rot is not None:
#             transform_rot(anim_rot.keyframes, bpy_obj.matrix_world.inverted())
#             transform_rot(anim_rot.keyframes, settings.global_matrix)
#
#         if geoset_anim is not None:
#             war3_model.geoset_anim_map[bone.name] = geoset_anim
#         war3_model.bones.append(bone)
#
#     mesh_geosets = set()
#
#     for matNameAnimTuple, tri_list in bpy_scene_objects.tri_list_map.items():
#         geoset = War3Geoset()
#         geoset.mat_name = matNameAnimTuple[0]
#         mesh_geosets.add(geoset)
#
#         vertex_color_anim = get_wc3_animation_curve(matNameAnimTuple[1][1][1], 'color', 3, war3_model.sequences)
#         vertex_color: Optional[Tuple[float]] = matNameAnimTuple[1][0]
#
#         geoset_anim: Optional[War3GeosetAnim] = None
#         geoset_anim_hash = 0
#         if any((vertex_color, vertex_color_anim, visibility)):
#             geoset_anim = War3GeosetAnim(vertex_color, vertex_color_anim, visibility)
#             geoset_anim_hash = hash(geoset_anim)  # The hash is a bit complex, so we precompute it
#
#         if geoset_anim is not None:
#             geoset.geoset_anim = geoset_anim
#             geoset_anim.geoset = geoset
#         bpy_vert_map: Dict[int, War3Vertex] = {}
#         vert_list: List[War3Vertex] = []
#         matrices: List[List[str]] = []
#         triangles: List[List[int]] = []
#         for tri in tri_list:
#             # UVs and materials
#             if settings.use_skinweights:
#                 geoset.skin_matrices = temp_skin_matrices
#
#             vertex_map: Dict[int, int] = {}
#             for vert, loop in zip(tri.vertices, tri.loops):
#                 if vert not in bpy_vert_map:
#                     vert_: bpy.types.MeshVertex = bpy_mesh.vertices[vert]
#                     bone_list, groups, weight_list = get_skinning(armature_mod, boneName, bone_names, bpy_obj, settings, vert_)
#
#                     if groups is not None and groups not in matrices:
#                         matrices.append(groups)
#                     matrix = 0 if 0 == matrices.count(groups) else matrices.index(groups)
#
#                     vertex = get_war3_vertex(bone_list, bpy_mesh, loop, matrix, tri, vert, vert_, weight_list)
#
#                     if vertex not in vert_list:
#                         vert_list.append(vertex)
#                     vertex_map[vert] = vert_list.index(vertex)
#                     bpy_vert_map[vert] = vertex
#                 else:
#                     vertex_map[vert] = vert_list.index(bpy_vert_map[vert])
#
#             # Triangles, normals, vertices, and UVs
#             triangles.append(
#                 [vertex_map[tri.vertices[0]], vertex_map[tri.vertices[1]], vertex_map[tri.vertices[2]]])
#         geoset.vertices.extend(vert_list)
#         geoset.matrices.extend(matrices)
#         geoset.triangles.extend(triangles)
#
#     for geoset in mesh_geosets:
#         # geoset.objects.append(bpy_obj)
#         if not len(geoset.matrices) and boneName is not None:
#             geoset.matrices.append([boneName])
#
#     # obj.to_mesh_clear()
#     bpy.data.meshes.remove(bpy_mesh)
#
#
# def get_war3_vertex(bone_list, bpy_mesh, loop, matrix, tri, vert, vert_, weight_list):
#     co = Vector(bpy_mesh.vertices[vert].co)
#     coord = [rnd(co.x), rnd(co.y), rnd(co.z)]
#     n = Vector(vert_.normal if tri.use_smooth else tri.normal)
#     norm = [rnd(n.x), rnd(n.y), rnd(n.z)]
#     uv = Vector(bpy_mesh.uv_layers.active.data[loop].uv) if len(bpy_mesh.uv_layers) else Vector((0.0, 0.0))
#     tvert = [rnd(uv.x),
#              rnd(1 - uv.y)]  # For some reason, uv Y coordinates appear flipped. This should fix that
#     vertex = War3Vertex(coord, norm, tvert, matrix, bone_list, weight_list, None)
#     return vertex
#
#
# def get_skinning(armature_mod: Optional[ArmatureModifier],
#                  boneName: str,
#                  bone_names: Set[str],
#                  bpy_obj: bpy.types.Object,
#                  settings: War3ExportSettings,
#                  vert_: bpy.types.MeshVertex) \
#         -> Tuple[Optional[List[str]], Optional[List[str]], Optional[List[int]]]:
#     groups: Optional[List[str]] = None
#     skins = None
#     bone_list: Optional[List[str]] = None
#     weight_list: Optional[List[int]] = None
#     vertex_groups: List[VertexGroupElement] = []
#     if armature_mod is not None:
#         vertex_groups = sorted(vert_.groups[:], key=lambda x: x.weight, reverse=True)
#         # Sort bones by descending weight
#     if settings.use_skinweights:
#         # skins = get_skins(bone_names, geoset, bpy_obj, vertex_groups)
#         if len(vertex_groups):
#             bone_list, weight_list = get_skins2(bone_names, bpy_obj.vertex_groups, vertex_groups)
#
#     else:
#         if len(vertex_groups):
#             groups = get_matrix_groups(boneName, bone_names, bpy_obj, vertex_groups)
#     return bone_list, groups, weight_list
#
#
# def get_arm_mod(bpy_obj: bpy.types.Object) -> Optional[ArmatureModifier]:
#     for m in bpy_obj.modifiers:
#         if m.type == 'ARMATURE':
#             return m
#     return None
#
#
# def get_matrix_groups(boneName, bone_names, bpy_obj, vertex_groups):
#     all_vgs: List[bpy.types.VertexGroup] = bpy_obj.vertex_groups
#     # Warcraft 800 does not support vertex weights, so we exclude groups with too small influence
#     groups = list(all_vgs[vg.group].name for vg in vertex_groups if
#                   (all_vgs[vg.group].name in bone_names and vg.weight > 0.25))[:3]
#     if not len(groups):
#         for vg in vertex_groups:
#             # If we didn't find a group, just take the best match (the list is already sorted by weight)
#             if all_vgs[vg.group].name in bone_names:
#                 groups = [all_vgs[vg.group].name]
#                 break
#     if boneName is not None and (groups is None or len(groups) == 0):
#         groups = [boneName]
#     return groups
#
#
# def get_skins2(bone_names: Set[str], all_vgs: List[bpy.types.VertexGroup], vertex_groups: List[VertexGroupElement])\
#         -> Tuple[List[str], List[int]]:
#     # Warcraft 800+ do support vertex (skin) weights; 4 per vertex which sum up to 255
#     bone_list = (list(all_vgs[vg.group].name for vg in vertex_groups if (all_vgs[vg.group].name in bone_names)))[:4]
#     weight_list = (list(vg.weight for vg in vertex_groups if (all_vgs[vg.group].name in bone_names)) + [0] * 4)[:4]
#
#     tot_weight = sum(weight_list)
#     w_conv = 255 / tot_weight
#     weight_list = [round(i * w_conv) for i in weight_list]
#     # Ugly fix to make sure total weight is 255
#
#     weight_adjust = 255 - sum(weight_list)
#     weight_list[0] = int(weight_list[0] + weight_adjust)
#     # skins = bone_list + weight_list
#     return bone_list, weight_list
#
#
# def get_geoset_anim(obj: bpy.types.Object, visibility: Optional[War3AnimationCurve], war3_model: War3Model)\
#         -> Tuple[Optional[War3GeosetAnim], int]:
#     vertex_color_anim = get_wc3_animation_curve(obj.animation_data, 'color', 3, war3_model.sequences)
#     vertex_color = None
#     if any(i < 0.999 for i in obj.color[:3]):
#         vertex_color = tuple(obj.color[:3])
#     if not any((vertex_color, vertex_color_anim)):
#         mat = obj.active_material
#         if mat is not None and hasattr(mat, "node_tree") and mat.node_tree is not None:
#             node = mat.node_tree.nodes.get("VertexColor")
#             if node is not None:
#                 attr = "outputs" if node.bl_idname == 'ShaderNodeRGB' else "inputs"
#                 vertex_color = tuple(getattr(node, attr)[0].default_value[:3])
#                 if hasattr(mat.node_tree, "animation_data"):
#                     vertex_color_anim = get_wc3_animation_curve(
#                         mat.node_tree.animation_data, 'nodes["VertexColor"].%s[0].default_value' % attr, 3,
#                         war3_model.sequences)
#     geoset_anim: Optional[War3GeosetAnim] = None
#     geoset_anim_hash = 0
#     if any((vertex_color, vertex_color_anim, visibility)):
#         geoset_anim = War3GeosetAnim(vertex_color, vertex_color_anim, visibility)
#         geoset_anim_hash = hash(geoset_anim)  # The hash is a bit complex, so we precompute it
#     return geoset_anim, geoset_anim_hash
#
#
# def create_geoset(bpy_geoset: BpyGeoset, bone_names: List[str]) -> War3Geoset:
#     geoset = War3Geoset()
#     geoset.mat_name = bpy_geoset.material_name
#
#     geoset_anim: Optional[War3GeosetAnim] = None
#     # geoset.matrices.extend(matrices)
#
#     if geoset_anim is not None:
#         geoset.geoset_anim = geoset_anim
#         geoset_anim.geoset = geoset
#
#     for v_key, v_index in bpy_geoset.vertex_map.items():
#         matrix = []
#         for bone_name in bpy_geoset.bone_list[v_index]:
#             if bone_name in bone_names:
#                 matrix.append(bone_name)
#         if matrix not in geoset.matrices:
#             geoset.matrices.append(matrix)
#         vertex_group_index = 0 if not len(matrix) or geoset.matrices.count(matrix) else geoset.matrices.index(matrix)
#         vertex = War3Vertex(bpy_geoset.pos_list[v_index],
#                             bpy_geoset.normal_list[v_index],
#                             bpy_geoset.uv_list[v_index], vertex_group_index,
#                             bpy_geoset.bone_list[v_index],
#                             bpy_geoset.weight_list[v_index],
#                             bpy_geoset.tangent_list[v_index])
#         geoset.vertices.append(vertex)
#
#     for tri_bpy, tri_war3 in bpy_geoset.tri_map.items():
#         geoset.triangles.append(list(tri_war3))
#
#     return geoset
#
#
#
#
#
#
