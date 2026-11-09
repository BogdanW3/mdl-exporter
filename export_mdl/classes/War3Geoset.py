from typing import TextIO, List, Dict, Optional

from .War3Bone import War3Bone
from .War3GeosetAnim import War3GeosetAnim
from .War3Vertex import War3Vertex
from ..utils import float2str, calc_bounds_radius


class War3Geoset:
    def __init__(self):
        self.vertices: List[War3Vertex] = []
        self.triangles: List[List[int]] = []
        self.matrices: List[List[str]] = []
        self.min_extent = None
        self.max_extent = None
        self.mat_name: Optional[str] = None
        self.name: Optional[str] = None
        self.geoset_anim: Optional[War3GeosetAnim] = None

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.mat_name == other.mat_name and self.geoset_anim == other.geoset_anim
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return hash(tuple(sorted(self.__dict__.items())))
        return hash((self.mat_name, hash(self.geoset_anim)))  # Different geoset anims should split geosets

    def skin_matrices(self, bone_ids: Dict[str, int]):
        """For skinned geosets: the node ids the geoset's matrix list holds (one single-bone group each, like
        Blizzard's), and per vertex the four skin bone indices. Skin bone indices are positions in that list, not
        node ids (HiveWE mdx.ixx); Blizzard's lists are mostly 0, 1, 2..., which hides the difference."""
        ids = sorted({bone_ids.get(name, 0) for vertex in self.vertices
                      for name, weight in zip(vertex.bone_list, vertex.weight_list) if weight}) or [0]
        position = {node_id: i for i, node_id in enumerate(ids)}
        skins = []
        for vertex in self.vertices:
            bones = [position.get(bone_ids.get(name, 0), 0) if weight else 0
                     for name, weight in zip(vertex.bone_list, vertex.weight_list)]
            skins.append((bones + [0, 0, 0, 0])[:4])
        return ids, skins

    def write_geoset(self, fw: TextIO.write, material_names,
                     sequences,
                     bones: List[War3Bone],
                     use_skinweights: bool):
        fw("Geoset {\n")
        # Vertices
        fw("\tVertices %d {\n" % len(self.vertices))
        for vertex in self.vertices:
            fw("\t\t{ %s, %s, %s },\n" % tuple(map(float2str, vertex.pos)))
        fw("\t}\n")
        # Normals
        fw("\tNormals %d {\n" % len(self.vertices))
        for vertex in self.vertices:
            fw("\t\t{ %s, %s, %s },\n" % tuple(map(float2str, vertex.normal)))
        fw("\t}\n")

        # TVertices
        fw("\tTVertices %d {\n" % len(self.vertices))
        for vertex in self.vertices:
            fw("\t\t{ %s, %s },\n" % tuple(map(float2str, vertex.uv)))
        fw("\t}\n")

        object_indices: Dict[str, int] = {}
        for bone in bones:
            object_indices[bone.name] = bone.obj_id
        # VertexGroups
        fw("\tVertexGroup {\n")
        if not use_skinweights:
            for vertex in self.vertices:
                if self.matrices.count(vertex.bone_list):
                    fw("\t\t%d,\n" % self.matrices.index(vertex.bone_list))
                else:
                    fw("\t\t%d,\n" % 0)
        fw("\t}\n")

        if use_skinweights:
            # Tangents
            fw("\tTangents %d {\n" % len(self.vertices))
            for vertex in self.vertices:
                tangents = tuple(vertex.tangent)
                fw("\t\t{ %s, %s, %s, %s },\n" % tuple(tangents))
            fw("\t}\n")
            # SkinWeights
            skin_ids, skins = self.skin_matrices(object_indices)
            fw("\tSkinWeights %d {\n" % len(self.vertices))
            for vertex, bones in zip(self.vertices, skins):
                fw("\t\t%s, %s, %s, %s, " % tuple(bones))
                weights = list(vertex.weight_list)
                weights.extend([0, 0, 0, 0])
                fw("%s, %s, %s, %s,\n" % tuple(weights[0:4]))
            fw("\t}\n")

        # Faces
        fw("\tFaces %d %d {\n" % (1, len(self.triangles) * 3))

        fw("\t\tTriangles {\n")
        fw("\t\t\t{ ")

        all_triangles = []
        for triangle in self.triangles:
            for index in triangle:
                all_triangles.append(str(index))
        fw(", ".join(all_triangles))
        fw(" },\n")
        fw("\t\t}\n")
        fw("\t}\n")

        if use_skinweights:
            # The skin weights' bone indices are positions in this list
            fw("\tGroups %d %d {\n" % (len(skin_ids), len(skin_ids)))
            for obj_id in skin_ids:
                fw("\t\tMatrices { %d },\n" % obj_id)
            fw("\t}\n")
        else:
            fw("\tGroups %d %d {\n" % (len(self.matrices), sum(len(mtrx) for mtrx in self.matrices)))
            for matrix in self.matrices:
                fw("\t\tMatrices { %s },\n" % ','.join(str(object_indices.get(g, 0)) for g in matrix))
            fw("\t}\n")

        fw("\tMinimumExtent { %s, %s, %s },\n" % tuple(map(float2str, self.min_extent)))
        fw("\tMaximumExtent { %s, %s, %s },\n" % tuple(map(float2str, self.max_extent)))
        fw("\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(self.min_extent, self.max_extent)))

        for sequence in sequences:
            fw("\tAnim {\n")

            # As of right now, we just use the self bounds.
            fw("\t\tMinimumExtent { %s, %s, %s },\n" % tuple(map(float2str, self.min_extent)))
            fw("\t\tMaximumExtent { %s, %s, %s },\n" % tuple(map(float2str, self.max_extent)))
            fw("\t\tBoundsRadius %s,\n" % float2str(calc_bounds_radius(self.min_extent, self.max_extent)))

            fw("\t}\n")

        fw("\tMaterialID %d,\n" % material_names.index(self.mat_name))

        fw("}\n")
