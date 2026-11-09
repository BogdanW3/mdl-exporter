from typing import List, Dict, Tuple, Optional

import bpy
from export_mdl.classes.model_utils.get_parent_name import get_parent_name


class BpyGeoset:
    def __init__(self, bpy_mesh: bpy.types.Mesh, bpy_obj: bpy.types.Object, material_slot: int, bone_names: List[str],
                 split_tangents: bool = True):
        # self.vertex_list: List[int] = []  # indices
        self.name = bpy_obj.name
        print("Processing BpyGeoset - name:", self.name)
        self.bpy_mesh: bpy.types.Mesh = bpy_mesh
        self.bpy_obj: bpy.types.Object = bpy_obj
        self.material_slot: int = material_slot
        self.bpy_material: Optional[bpy.types.Material] = None
        self.material_name: str = "default"
        if bpy_mesh.materials:
            self.bpy_material: Optional[bpy.types.Material] = bpy_mesh.materials[material_slot]
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
        # self.self_as_parent: bool = bpy_obj.parent is None and bpy_obj.animation_data is not None and all_vgs
        self.no_vgs: bool = not all_vgs
        self.self_as_parent: bool = bpy_obj.parent is None and not all_vgs
        self.parent_name: Optional[str] = get_parent_name(bpy_obj)
        # print("geoset has self as parent:", self.self_as_parent)

        # Per-corner normals carry custom normals, flat shading and sharp edges; vertex normals are always the
        # smooth average. Blender 4.1+ has Mesh.corner_normals, older versions loop.normal after calc_normals_split.
        corner_normals = getattr(bpy_mesh, 'corner_normals', None)
        has_tangents = bool(bpy_mesh.uv_layers)
        normal_groups: Dict[str, list] = {}
        twin_layer = bpy_mesh.attributes.get("mdl_vertex_twin") if hasattr(bpy_mesh, "attributes") else None
        twins = None
        if twin_layer is not None and twin_layer.domain == 'POINT' and len(twin_layer.data) == len(bpy_mesh.vertices):
            twins = [0] * len(bpy_mesh.vertices)
            twin_layer.data.foreach_get("value", twins)

        for tri in bpy_mesh.loop_triangles:
            if tri.material_index is material_slot:
                tri_vert_map: Dict[int, int] = {}
                for vert_index, loop in zip(tri.vertices, tri.loops):
                    vertex = bpy_mesh.vertices[vert_index]
                    normal = tuple(corner_normals[loop].vector) if corner_normals is not None \
                        else tuple(bpy_mesh.loops[loop].normal)
                    # A copy the importer made (a double-sided face on the same vertices) is its original again
                    twin_index = twins[vert_index] if twins is not None and twins[vert_index] >= 0 else vert_index
                    vert_int_s = "%s, " % twin_index
                    pos_s = "%s, %s, %s, " % tuple(vertex.undeformed_co)
                    mesh_uv_layers = bpy_mesh.uv_layers
                    uv: List[float] = [0.0, 0.0] \
                        if not len(mesh_uv_layers) \
                        else mesh_uv_layers.active.data[loop].uv
                    uv[1] = 1 - uv[1]
                    # blender [0,0],[1,1] = [bottom left, top right],
                    # warcraft3 [0,0],[1,1] = [top left, bottom right]
                    uv_s = "%s, %s" % tuple(uv)
                    if has_tangents:
                        bpy_loop = bpy_mesh.loops[loop]
                        # Handedness as Blender computes it matches Blizzard's files (checked against Reforged
                        # models), V flip included
                        tangent: List[float] = list(bpy_loop.tangent) + [bpy_loop.bitangent_sign]
                    else:
                        tangent = [0.7, 0.7, 0.0, 1.0]
                    base_key = vert_int_s + pos_s + uv_s
                    if split_tangents:
                        base_key += ", %d" % tangent[3]
                    # Corners of one vertex share an exported vertex when their normals agree. (Not by comparing
                    # rounded text: custom normals decode a hair differently per corner, -0.000 isn't 0.000...)
                    same_spot = normal_groups.setdefault(base_key, [])
                    vertex_key = next((key for other, key in same_spot
                                       if max(abs(a - b) for a, b in zip(other, normal)) < 1e-3), None)
                    if vertex_key is None:
                        vertex_key = base_key + " #%d" % len(same_spot)
                        same_spot.append((normal, vertex_key))
                    if vertex_key not in self.vertex_map:
                        self.vertex_map[vertex_key] = len(self.vertex_list)
                        self.vertex_list.append(vertex)
                        self.pos_list.append(vertex.undeformed_co)
                        self.normal_list.append(normal)
                        self.tangent_list.append(tangent)
                        self.uv_list.append(uv)
                        vertex_groups: List[bpy.types.VertexGroupElement] = sorted(vertex.groups[:], key=lambda x: x.weight, reverse=True)
                        if all_vgs:
                            bones = []
                            weights = []
                            for vg in vertex_groups:
                                if vg.weight != 0 and all_vgs[vg.group].name in bone_names:
                                    bones.append(all_vgs[vg.group].name)
                                    weights.append(vg.weight)
                            if bones:
                                self.bone_list.append(bones)
                                self.weight_list.append(self.get_int_weights(weights))
                            else:
                                if self.self_as_parent:
                                    self.bone_list.append([self.name])
                                elif self.no_vgs:
                                    self.bone_list.append([self.parent_name])
                                else:
                                    self.bone_list.append([""])
                                # should this be 255..?
                                self.weight_list.append([255])

                            # self.bone_list.append(list(all_vgs[vg.group].name for vg in vertex_groups if vg.weight != 0 and all_vgs[vg.group].name in bone_names))
                            # self.weight_list.append(self.get_int_weights(list(vg.weight for vg in vertex_groups if vg.weight != 0 and all_vgs[vg.group].name in bone_names)))
                        else:
                            if self.self_as_parent:
                                self.bone_list.append([self.name])
                            elif self.no_vgs:
                                self.bone_list.append([self.parent_name])
                            else:
                                self.bone_list.append([""])
                            # should this be 255..?
                            self.weight_list.append([255])

                    tri_vert_map[vert_index] = self.vertex_map[vertex_key]
                self.tri_map[tuple(tri.loops)] = tuple([tri_vert_map[v] for v in tri.vertices])


    def get_int_weights(self, weights: List[float]) -> List[int]:
        # Warcraft 800+ do support vertex (skin) weights; 4 per vertex which sum up to 255
        tot_weight = sum(weights[:min(4, len(weights))])
        w_conv = 255.0 / tot_weight
        weight_list = [round(i * w_conv) for i in weights]
        # Ugly fix to make sure total weight is 255

        weight_adjust = int(255.0 - sum(weight_list[:min(4, len(weights))]))
        weight_list[0] = int(weight_list[0] + weight_adjust)
        return weight_list

    def get_path(self):
        return 'bpy.data.materials["{0}"]'.format(self.material_name)

    def get_geo_color_path(self):
        # return self.get_path() + '.node_tree.nodes["Geoset Anim Color"].outputs[0].default_value'
        return self.get_path() + '.node_tree.nodes["Geoset Anim Color"].outputs[0]'

    def get_geo_alpha_path(self):
        # return self.get_path() + '.node_tree.nodes["Geoset Anim Alpha"].inputs[1].default_value'
        return self.get_path() + '.node_tree.nodes["Geoset Anim Alpha"].inputs[1]'
