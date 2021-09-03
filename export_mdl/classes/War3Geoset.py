from typing import TextIO, List

from .War3Vertex import War3Vertex
from ..utils import f2s, calc_bounds_radius


class War3Geoset:
    def __init__(self):
        self.vertices: List[War3Vertex] = []
        self.triangles: [float] = []
        self.matrices = []
        self.skin_matrices = []
        self.skin_weights = []
        self.objects = []
        self.min_extent = None
        self.max_extent = None
        self.mat_name = None
        self.geoset_anim = None

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.mat_name == other.mat_name and self.geoset_anim == other.geoset_anim
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return hash(tuple(sorted(self.__dict__.items())))
        return hash((self.mat_name, hash(self.geoset_anim)))  # Different geoset anims should split geosets

    def write_geoset(self, fw: TextIO.write, material_names, sequences, object_indices, settings):
        fw("Geoset {\n")
        # Vertices
        fw("\tVertices %d {\n" % len(self.vertices))
        for vertex in self.vertices:
            fw("\t\t{%s, %s, %s},\n" % tuple(map(f2s, vertex.pos)))
        fw("\t}\n")
        # Normals
        fw("\tNormals %d {\n" % len(self.vertices))
        for vertex in self.vertices:
            fw("\t\t{%s, %s, %s},\n" % tuple(map(f2s, vertex.normal)))
        fw("\t}\n")

        # TVertices
        fw("\tTVertices %d {\n" % len(self.vertices))
        for vertex in self.vertices:
            fw("\t\t{%s, %s},\n" % tuple(map(f2s, vertex.uv)))
        fw("\t}\n")

        # VertexGroups
        fw("\tVertexGroup {\n")

        if not settings.use_skinweights:
            for vertex in self.vertices:
                fw("\t\t%d,\n" % vertex.matrix)
        fw("\t}\n")

        if settings.use_skinweights:
            # Tangents
            fw("\tTangents %d {\n" % len(self.vertices))
            for vertex in self.vertices:
                # fw("\t\t{%s, %s, %s, -1},\n" % tuple(map(f2s, vertex[1])))
                tangents = tuple(map(f2s, vertex.normal)) + tuple({str(sum(vertex.normal) / abs(sum(vertex.normal)))})
                fw("\t\t{%s, %s, %s, %s},\n" % tuple(tangents))
            fw("\t}\n")
            # SkinWeights
            fw("\tSkinWeights %d {\n" % len(self.vertices))
            for vertex in self.vertices:
                fw("\t\t%s, %s, %s, %s, %s, %s, %s, %s,\n" % tuple(vertex.skin))
            fw("\t}\n")

        # Faces
        # fw("\tFaces %d %d {\n" % (len(self.triangles), len(self.triangles) * 3))
        fw("\tFaces %d %d {\n" % (1, len(self.triangles) * 3))

        fw("\t\tTriangles {\n")
        fw("\t\t\t{")
        # for triangle in self.triangles:
        #     fw(" %d, %d, %d," % triangle[:])

        all_triangles = []
        for triangle in self.triangles:
            for index in triangle:
                all_triangles.append(str(index))
        fw(", ".join(all_triangles))
        # fw("\t\t\t},\n")
        fw("},\n")
        fw("\t\t}\n")
        # fw("\t\tTriangles {\n")
        # for triangle in self.triangles:
        #     fw("\t\t\t{%d, %d, %d},\n" % triangle[:])
        # fw("\t\t}\n")
        fw("\t}\n")

        fw("\tGroups %d %d {\n" % (len(self.matrices), sum(len(mtrx) for mtrx in self.matrices)))
        for matrix in self.matrices:
            fw("\t\tMatrices {%s},\n" % ','.join(str(object_indices[g]) for g in matrix))
        fw("\t}\n")

        fw("\tMinimumExtent {%s, %s, %s},\n" % tuple(map(f2s, self.min_extent)))
        fw("\tMaximumExtent {%s, %s, %s},\n" % tuple(map(f2s, self.max_extent)))
        fw("\tBoundsRadius %s,\n" % f2s(calc_bounds_radius(self.min_extent, self.max_extent)))

        for sequence in sequences:
            fw("\tAnim {\n")

            # As of right now, we just use the self bounds.
            fw("\t\tMinimumExtent {%s, %s, %s},\n" % tuple(map(f2s, self.min_extent)))
            fw("\t\tMaximumExtent {%s, %s, %s},\n" % tuple(map(f2s, self.max_extent)))
            fw("\t\tBoundsRadius %s,\n" % f2s(calc_bounds_radius(self.min_extent, self.max_extent)))

            fw("\t}\n")

        fw("\tMaterialID %d,\n" % material_names.index(self.mat_name))

        fw("}\n")
