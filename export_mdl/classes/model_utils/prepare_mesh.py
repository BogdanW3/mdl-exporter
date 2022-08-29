import bmesh
import bpy
from bpy.types import Mesh


def prepare_mesh(bpy_obj: bpy.types.Object, context: bpy.context, matrix) -> Mesh:
    mod = None
    if bpy_obj.data.use_auto_smooth:
        mod = bpy_obj.modifiers.new("EdgeSplitExport", 'EDGE_SPLIT')
        mod.split_angle = bpy_obj.data.auto_smooth_angle
        # mod.use_edge_angle = True

    deps_graph = context.evaluated_depsgraph_get()
    bpy_mesh = bpy.data.meshes.new_from_object(bpy_obj.evaluated_get(deps_graph), preserve_all_data_layers=True, depsgraph=deps_graph)

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

    return bpy_mesh
