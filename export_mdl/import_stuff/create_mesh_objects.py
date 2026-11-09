from typing import List, Dict

import bpy

from export_mdl.classes.War3Geoset import War3Geoset
from export_mdl.classes.War3Model import War3Model
from export_mdl.import_stuff.War3BpyMaterial import War3BpyMaterial


def create_mesh_objects(model: War3Model,
                        bpy_armature_object: bpy.types.Object,
                        bpy_materials: Dict[str, War3BpyMaterial]):
    # print("Geosets")
    print(" creating meshes")
    bpy_mesh_objects = []

    for war3_geoset in model.geosets:
        mesh_name = model.name if war3_geoset.name is None else war3_geoset.name
        if mesh_name.isnumeric():
            mesh_name = mesh_name + " " + model.name
        print("  Geoset \"" + mesh_name + "\"")
        # print("  creating mesh for \"" + mesh_name + "\"")
        print("   creating mesh")
        # print("creating geoset: ", mesh_name)
        bpy_mesh = bpy.data.meshes.new(mesh_name)
        # print("new object for ", mesh_name)
        bpy_object = bpy.data.objects.new(mesh_name, bpy_mesh)
        # print("adding ", mesh_name, "to scene")
        bpy.context.scene.collection.objects.link(bpy_object)
        # print("collecting positions for %s verts" % len(war3_geoset.vertices))
        locations = [v.pos for v in war3_geoset.vertices]
        # for l in locations:
        #     print(l)

        # print("creating mesh with %s verts" % len(locations))
        # Some Reforged models have zero-area triangles that repeat a vertex. Blender doesn't allow those,
        # and 5.3 hangs in bmesh operations on meshes that have them.
        triangles = [t for t in war3_geoset.triangles if len(set(t)) == 3]
        bpy_mesh.from_pydata(locations, (), triangles)

        # print("applying uvs")
        apply_uvs(bpy_mesh, war3_geoset)

        # Keep the model's own normals as custom normals, so they survive a round trip
        bpy_mesh.polygons.foreach_set("use_smooth", [True] * len(bpy_mesh.polygons))
        if hasattr(bpy_mesh, 'use_auto_smooth'):
            bpy_mesh.use_auto_smooth = True  # Custom normals need this before Blender 4.1
        bpy_mesh.normals_split_custom_set_from_vertices([tuple(v.normal) for v in war3_geoset.vertices])

        bpy_material = bpy_materials[war3_geoset.mat_name]
        bpy_mesh.materials.append(bpy_material.bpy_material)

        # print("making bone groups")
        for bone in model.bones:
            bpy_object.vertex_groups.new(name=str(bone.name))

        # print("applying bones")
        print("   skinning")
        groups: bpy.types.VertexGroups = bpy_object.vertex_groups
        for vertex_index, vertex in enumerate(war3_geoset.vertices):
            for i in range(0, len(vertex.bone_list)):
                if vertex.weight_list[i] != 0:
                    v_bone = vertex.bone_list[i]
                    # print("bone:", v_bone, "weight", (vertex.weight_list[i] / 255.0))

                    vert_group: bpy.types.VertexGroup = groups.get(v_bone)
                    if vert_group is None:
                        # HD skins can weight to any node, not only bones
                        vert_group = groups.new(name=str(v_bone))
                    vert_group.add([vertex_index, ], vertex.weight_list[i] / 255.0, 'REPLACE')
                    # bpy_object.vertex_groups.get(vertex.bone_list[i]).add([vertex_index, ], vertex.weight_list[i] / 255.0, 'REPLACE')

        bpy_object.modifiers.new(name='Armature', type='ARMATURE')
        bpy_object.modifiers['Armature'].object = bpy_armature_object
        bpy_mesh_objects.append(bpy_object)
    return bpy_mesh_objects


def apply_uvs(bpy_mesh: bpy.types.Mesh, war3_geoset: War3Geoset):
    # print("applying uvs")
    bpy_mesh.uv_layers.new()
    uv_layer = bpy_mesh.uv_layers.active.data
    for tris in bpy_mesh.polygons:
        for loopIndex in range(tris.loop_start, tris.loop_start + tris.loop_total):
            vertex_index = bpy_mesh.loops[loopIndex].vertex_index
            uv_layer[loopIndex].uv = war3_geoset.vertices[vertex_index].uv
