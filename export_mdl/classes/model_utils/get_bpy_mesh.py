import bmesh
import bpy
from bpy.types import Mesh


def get_bpy_mesh(bpy_obj: bpy.types.Object, context: bpy.context, matrix) -> Mesh:
    mod = None
    if bpy_obj.data.use_auto_smooth:
        mod = bpy_obj.modifiers.new("EdgeSplitExport", 'EDGE_SPLIT')
        mod.split_angle = bpy_obj.data.auto_smooth_angle
        # mod.use_edge_angle = True

    arm_mod = None
    arm_show_r = True
    arm_show_v = True
    if bpy_obj.find_armature():
        for mod_ in bpy_obj.modifiers:
            if mod_.type == 'ARMATURE':
                arm_mod = mod_
                break

    if arm_mod is not None:
        # to make sure that we are not exporting the mesh in an animated state
        arm_show_r = arm_mod.show_render
        arm_show_v = arm_mod.show_viewport
        arm_mod.show_render = False
        arm_mod.show_viewport = False

    deps_graph = context.evaluated_depsgraph_get()
    bpy_mesh = bpy.data.meshes.new_from_object(bpy_obj.evaluated_get(deps_graph), preserve_all_data_layers=True, depsgraph=deps_graph)

    if arm_mod is not None:
        arm_mod.show_render = arm_show_r
        arm_mod.show_viewport = arm_show_v

    if bpy_obj.data.use_auto_smooth:
        bpy_obj.modifiers.remove(mod)

    # Triangulate for web export
    bm = bmesh.new()
    bm.from_mesh(bpy_mesh)

    # If an object has had a negative scale applied, normals will be inverted. This will fix that.
    if any(s < 0 for s in bpy_obj.scale):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bm.to_mesh(bpy_mesh)
    bm.free()
    del bm

    bpy_mesh.calc_normals_split()
    bpy_mesh.calc_loop_triangles()

    layer = bpy_mesh.uv_layers[0]
    if layer \
            and (hasattr(layer, "uv") and layer.uv
                 or hasattr(layer, "data") and layer.data
                 and hasattr(layer.data, "uv") and layer.data.uv):
        bpy_mesh.calc_tangents()
    #
    # if(len(bpy_mesh.materials) == 0):
    #     bpy_mesh.materials.

    return bpy_mesh


def get_bpy_curve_mesh(bpy_obj: bpy.types.Object, context: bpy.context, matrix) -> Mesh:
    mod = None
    # if bpy_obj.data.use_auto_smooth:
    #     mod = bpy_obj.modifiers.new("EdgeSplitExport", 'EDGE_SPLIT')
    #     mod.split_angle = bpy_obj.data.auto_smooth_angle
    #     # mod.use_edge_angle = True

    arm_mod = None
    arm_show_r = True
    arm_show_v = True
    if bpy_obj.find_armature():
        for mod_ in bpy_obj.modifiers:
            if mod_.type == 'ARMATURE':
                arm_mod = mod_
                break

    if arm_mod is not None:
        # to make sure that we are not exporting the mesh in an animated state
        arm_show_r = arm_mod.show_render
        arm_show_v = arm_mod.show_viewport
        arm_mod.show_render = False
        arm_mod.show_viewport = False

    deps_graph = context.evaluated_depsgraph_get()
    bpy_mesh = bpy.data.meshes.new_from_object(bpy_obj.evaluated_get(deps_graph), preserve_all_data_layers=True, depsgraph=deps_graph)

    if arm_mod is not None:
        arm_mod.show_render = arm_show_r
        arm_mod.show_viewport = arm_show_v

    # if bpy_obj.data.use_auto_smooth:
    #     bpy_obj.modifiers.remove(mod)

    # Triangulate for web export
    bm = bmesh.new()
    bm.from_mesh(bpy_mesh)

    # If an object has had a negative scale applied, normals will be inverted. This will fix that.
    if any(s < 0 for s in bpy_obj.scale):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bm.to_mesh(bpy_mesh)
    bm.free()
    del bm

    bpy_mesh.calc_normals_split()
    bpy_mesh.calc_loop_triangles()
    bpy_mesh.calc_tangents()
    #
    # if(len(bpy_mesh.materials) == 0):
    #     bpy_mesh.materials.

    return bpy_mesh
