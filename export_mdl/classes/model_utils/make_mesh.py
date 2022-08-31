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
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec, transform_vec1
from ...utils import rnd


def make_mesh(war3_model: War3Model,
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
    bpy_mesh: Mesh = get_bpy_mesh(bpy_obj, context, settings.global_matrix @ bpy_obj.matrix_world)

    # Geoset Animation
    geoset_anim, geoset_anim_hash = get_geoset_anim(bpy_obj, visibility, war3_model)

    # armature_mod: Modifier = None
    armature_mod: Optional[ArmatureModifier] = None

    for m in bpy_obj.modifiers:
        if m.type == 'ARMATURE':
            armature_mod = m

    bone_names: Set[str] = set()
    if armature_mod is not None:
        bpy_armature: bpy.types.Object = armature_mod.object
        arm_data: bpy.types.Armature = bpy_armature.data
        # bone_names = set(b.name for b in armature_mod.object.data.bones)
        bone_names = set(b.name for b in arm_data.bones)

    # Make a list of all bones to use if saving skin weights
    temp_skin_matrices: Optional[List[List[str]]] = None
    if settings.use_skinweights:
        bpy_mesh.calc_tangents(bpy_mesh.uv_layers.active.name)
        if len(bone_names):
            bpy_armature: bpy.types.Object = armature_mod.object
            arm_data: bpy.types.Armature = bpy_armature.data
            temp_skin_matrices = list([b.name] for b in arm_data.bones)
            # temp_skin_matrices = list([b.name] for b in armature_mod.object.data.bones)

    pivot = settings.global_matrix @ Vector(bpy_obj.location)
    obj_name = bpy_obj.name
    boneName: Optional[str] = None
    if (armature_mod is None and parent_name is None) or any((anim_loc, anim_rot, anim_scale)):
        bone: War3Bone = War3Bone(obj_name, anim_loc, anim_rot, anim_scale, parent_name, pivot)
        bone.billboarded = billboarded
        bone.billboard_lock = billboard_lock
        boneName = bone.name

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
    material_slots = bpy_obj.material_slots
    print("bpy_mesh: ", bpy_mesh)
    print("bpy_mesh.loop_triangles: ", len(bpy_mesh.loop_triangles), bpy_mesh.loop_triangles)
    print("bpy_mesh.polygons: ", len(bpy_mesh.polygons), bpy_mesh.polygons)
    print("bpy_mesh.uv_layers: ", len(bpy_mesh.uv_layers), bpy_mesh.uv_layers)
    print("bpy_mesh.uv_layers[0]: ", len(bpy_mesh.uv_layers), bpy_mesh.uv_layers[0])
    loop_layer: bpy.types.MeshUVLoopLayer = bpy_mesh.uv_layers[0]
    print("loop_layer: ", loop_layer)
    print("loop_layer.data: ", len(loop_layer.data), loop_layer.data)
    print("loop_layer.data[0]: ", len(loop_layer.data), loop_layer.data[0])
    print("loop_layer.data[0].uv: ", len(loop_layer.data), loop_layer.data[0].uv)
    for tri in bpy_mesh.loop_triangles:
        # p = bpy_mesh.polygons[f.index]
        # UVs and materials
        material_name = "default"
        if material_slots and len(material_slots):
            bpy_material = material_slots[tri.material_index].material
            if bpy_material is not None:
                material_name = bpy_material.name
                mats.add(bpy_material)

        if (material_name, geoset_anim_hash) in war3_model.geoset_map.keys():
            geoset = war3_model.geoset_map[(material_name, geoset_anim_hash)]
        else:
            geoset = War3Geoset()
            geoset.mat_name = material_name
            if geoset_anim is not None:
                geoset.geoset_anim = geoset_anim
                geoset_anim.geoset = geoset

            war3_model.geoset_map[(material_name, geoset_anim_hash)] = geoset

        if settings.use_skinweights:
            geoset.skin_matrices = temp_skin_matrices

        vertex_map = get_vertex_map(armature_mod, boneName, bone_names, bpy_mesh, bpy_obj, geoset, settings, tri)

        # Triangles, normals, vertices, and UVs
        geoset.triangles.append(
            (vertex_map[tri.vertices[0]], vertex_map[tri.vertices[1]], vertex_map[tri.vertices[2]]))

        mesh_geosets.add(geoset)

    for geoset in mesh_geosets:
        # geoset.objects.append(bpy_obj)
        if not len(geoset.matrices) and boneName is not None:
            geoset.matrices.append([boneName])

    # obj.to_mesh_clear()
    bpy.data.meshes.remove(bpy_mesh)


def get_vertex_map(armature_mod: Optional[ArmatureModifier],
                   boneName: Optional[str],
                   bone_names: Set[str],
                   bpy_mesh: Mesh,
                   bpy_obj: bpy.types.Object,
                   geoset: War3Geoset,
                   settings: War3ExportSettings,
                   tri: MeshLoopTriangle) -> Dict[int, int]:
    # Vertices, faces, and matrices
    vertex_map = {}
    for vert, loop in zip(tri.vertices, tri.loops):
        co = bpy_mesh.vertices[vert].co
        coord = (rnd(co.x), rnd(co.y), rnd(co.z))
        n = bpy_mesh.vertices[vert].normal if tri.use_smooth else tri.normal
        norm = (rnd(n.x), rnd(n.y), rnd(n.z))
        uv = bpy_mesh.uv_layers.active.data[loop].uv if len(bpy_mesh.uv_layers) else Vector((0.0, 0.0))
        uv[1] = 1 - uv[1]  # For some reason, uv Y coordinates appear flipped. This should fix that.
        tvert = (rnd(uv.x), rnd(uv.y))
        groups: Optional[List[str]] = None
        skins = None
        bone_list = None
        weight_list = None
        matrix = 0
        if armature_mod is not None:
            vertex_groups: List[bpy.types.VertexGroupElement] = sorted(bpy_mesh.vertices[vert].groups[:], key=lambda x: x.weight, reverse=True)
            # Sort bones by descending weight
            if len(vertex_groups) and not settings.use_skinweights:
                groups = get_matrice_groups(bone_names, bpy_obj, vertex_groups)
            elif len(vertex_groups) and settings.use_skinweights:
                # skins = get_skins(bone_names, geoset, bpy_obj, vertex_groups)
                bone_list, weight_list = get_skins2(bone_names, bpy_obj, vertex_groups)

        if boneName is not None and (groups is None or len(groups) == 0):
            groups = [boneName]

        if groups is not None:
            if groups not in geoset.matrices:
                geoset.matrices.append(groups)
            matrix = geoset.matrices.index(groups)

        if settings.use_skinweights:
            # vertex = (coord, norm, tvert, skins)
            vertex = War3Vertex(coord, norm, tvert, None, bone_list, weight_list, None)
        else:
            # vertex = (coord, norm, tvert, matrix)
            # vertex = War3Vertex(coord, norm, tvert, matrix, None, None)
            vertex = War3Vertex(coord, norm, tvert, matrix, None, None, None)

        if vertex not in geoset.vertices:
            geoset.vertices.append(vertex)

        vertex_map[vert] = geoset.vertices.index(vertex)
    print("vertex_map: ", vertex_map)
    return vertex_map


def get_matrice_groups(bone_names: Set[str], obj: bpy.types.Object, vertex_groups: List[VertexGroupElement])\
        -> List[str]:
    # Warcraft 800 does not support vertex weights, so we exclude groups with too small influence
    all_vgs = obj.vertex_groups
    groups = list(all_vgs[vg.group].name for vg in vertex_groups if
                  (all_vgs[vg.group].name in bone_names and vg.weight > 0.25))[:3]
    if not len(groups):
        for vg in vertex_groups:
            # If we didn't find a group, just take the best match (the list is already sorted by weight)
            if all_vgs[vg.group].name in bone_names:
                groups = [all_vgs[vg.group].name]
                break
    return groups


def get_skins2(bone_names: Set[str], obj: bpy.types.Object, vertex_groups: List[VertexGroupElement])\
        -> Tuple[List[str], List[int]]:
    # Warcraft 800+ do support vertex (skin) weights; 4 per vertex which sum up to 255
    all_vgs = obj.vertex_groups
    bone_list = (list(all_vgs[vg.group].name for vg in vertex_groups if (all_vgs[vg.group].name in bone_names)))[:4]
    weight_list = (list(vg.weight for vg in vertex_groups if (all_vgs[vg.group].name in bone_names)) + [0] * 4)[:4]

    tot_weight = sum(weight_list)
    w_conv = 255 / tot_weight
    weight_list = [round(i * w_conv) for i in weight_list]
    # Ugly fix to make sure total weight is 255

    weight_adjust = 255 - sum(weight_list)
    weight_list[0] = int(weight_list[0] + weight_adjust)
    # skins = bone_list + weight_list
    return bone_list, weight_list


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


def create_bone_and_stuff(anim_loc: Optional[War3AnimationCurve],
                          anim_rot: Optional[War3AnimationCurve],
                          anim_scale: Optional[War3AnimationCurve],
                          armature,
                          billboard_lock,
                          billboarded,
                          pivot, name,
                          parent: Optional[str]) -> Optional[War3Bone]:

    if (armature is None and parent is None) or any((anim_loc, anim_rot, anim_scale)):
        bone: War3Bone = War3Bone(name, anim_loc, anim_rot, anim_scale, parent, pivot)
        bone.billboarded = billboarded
        bone.billboard_lock = billboard_lock

        return bone
    return None
