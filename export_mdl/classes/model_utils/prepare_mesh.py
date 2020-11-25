import bmesh
import bpy


def prepare_mesh(obj, context, matrix):
    mod = None
    if obj.data.use_auto_smooth:
        mod = obj.modifiers.new("EdgeSplitExport", 'EDGE_SPLIT')
        mod.split_angle = obj.data.auto_smooth_angle
        # mod.use_edge_angle = True

    deps_graph = context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(deps_graph), preserve_all_data_layers=True, depsgraph=deps_graph)

    if obj.data.use_auto_smooth:
        obj.modifiers.remove(mod)

    # Triangulate for web export
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # If an object has had a negative scale applied, normals will be inverted. This will fix that.
    if any(s < 0 for s in obj.scale):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    del bm

    mesh.calc_normals_split()
    mesh.calc_loop_triangles()

    return mesh
