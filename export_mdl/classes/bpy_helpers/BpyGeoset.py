from typing import List, Dict, Tuple, Optional

import bpy


class BpyGeoset:
    def __init__(self, bpy_mesh: bpy.types.Mesh, bpy_obj: bpy.types.Object, material_slot: int):
        # self.vertex_list: List[int] = []  # indices
        self.name = bpy_obj.name
        print("BpyGeoset - name:", self.name)
        self.bpy_mesh: bpy.types.Mesh = bpy_mesh
        self.material_slot: int = material_slot
        self.bpy_material: bpy.types.Material = bpy_mesh.materials[material_slot]
        self.material_name: str = bpy_mesh.materials[material_slot].name
        self.vertex_list: List[bpy.types.MeshVertex] = []  # vertices
        self.pos_list: List[List[float]] = []  # location
        self.normal_list: List[List[float]] = []  # normals
        self.tangent_list: List[List[float]] = []  # normals
        self.uv_list: List[List[float]] = []  # uv_coords
        self.vertex_map: Dict[str, int] = {}  # 'pos' + 'norm' + 'uv' to index in vertex_list
        self.tri_map: Dict[Tuple[int], Tuple[int]] = {}  # old vert indices to new
        self.bone_list: List[List[str]] = []
        self.weight_list: List[List[int]] = []

        all_vgs = bpy_obj.vertex_groups

        for tri in bpy_mesh.loop_triangles:
            if tri.material_index is material_slot:
                tri_vert_map: Dict[int, int] = {}
                for vert_index, loop in zip(tri.vertices, tri.loops):
                    vertex = bpy_mesh.vertices[vert_index]
                    vert_int_s = "%s, " % vert_index
                    # pos_s = "%s, %s, %s, " % tuple(vertex.co)
                    pos_s = "%s, %s, %s, " % tuple(vertex.undeformed_co)
                    norm_s = "%s, %s, %s, " % tuple(vertex.normal)
                    mesh_uv_layers = bpy_mesh.uv_layers
                    uv: List[float] = [0.0, 0.0] \
                        if not len(mesh_uv_layers) \
                        else mesh_uv_layers.active.data[loop].uv
                    uv[1] = 1 - uv[1]
                    # blender [0,0],[1,1] = [bottom left, top right],
                    # warcraft3 [0,0],[1,1] = [top left, bottom right]
                    uv_s = "%s, %s" % tuple(uv)
                    # tangent = bpy_mesh.loops[loop].tangent
                    tangent: List[float] = [0.7, 0.7, 0.0, 1.0] \
                        if not loop < len(bpy_mesh.loops) \
                        else list(bpy_mesh.loops[loop].tangent)
                    # print("tangent:", tangent)
                    if len(tangent) == 3:
                        tangent.append(1)
                    vertex_key = vert_int_s + pos_s + norm_s + uv_s
                    if vertex_key not in self.vertex_map:
                        self.vertex_map[vertex_key] = len(self.vertex_list)
                        self.vertex_list.append(vertex)
                        # self.pos_list.append(vertex.co)
                        self.pos_list.append(vertex.undeformed_co)
                        self.normal_list.append(vertex.normal)
                        self.tangent_list.append(tangent)
                        self.uv_list.append(uv)
                        vertex_groups: List[bpy.types.VertexGroupElement] = sorted(vertex.groups[:], key=lambda x: x.weight, reverse=True)
                        self.bone_list.append(list(all_vgs[vg.group].name for vg in vertex_groups if vg.weight != 0))
                        self.weight_list.append(self.get_int_weights(list(vg.weight for vg in vertex_groups if vg.weight != 0)))

                    tri_vert_map[vert_index] = self.vertex_map[vertex_key]
                # new_tri = (tri_vert_map[tri.vertices[0]], tri_vert_map[tri.vertices[1]], tri_vert_map[tri.vertices[2]])
                self.tri_map[tuple(tri.vertices)] = tuple([tri_vert_map[v] for v in tri.vertices])


    def get_int_weights(self, weights: List[float]) -> List[int]:
        # Warcraft 800+ do support vertex (skin) weights; 4 per vertex which sum up to 255

        tot_weight = sum(weights)
        w_conv = 255 / tot_weight
        weight_list = [round(i * w_conv) for i in weights]
        # Ugly fix to make sure total weight is 255

        weight_adjust = 255 - sum(weight_list)
        weight_list[0] = int(weight_list[0] + weight_adjust)
        # skins = bone_list + weight_list
        return weight_list

    def get_path(self):
        return 'bpy.data.materials["{0}"]'.format(self.material_name)

    def get_geo_color_path(self):
        # return self.get_path() + '.node_tree.nodes["Geoset Anim Color"].outputs[0].default_value'
        return self.get_path() + '.node_tree.nodes["Geoset Anim Color"].outputs[0]'

    def get_geo_alpha_path(self):
        # return self.get_path() + '.node_tree.nodes["Geoset Anim Alpha"].inputs[1].default_value'
        return self.get_path() + '.node_tree.nodes["Geoset Anim Alpha"].inputs[1]'
