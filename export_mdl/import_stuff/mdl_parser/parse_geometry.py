from typing import List

from .mdl_reader import chunkifier, extract_bracket_content, extract_float_values, extract_int_values

from .get_vertex_groups import get_vertex_groups
from ...classes.War3Geoset import War3Geoset
from ...classes.War3Vertex import War3Vertex


def parse_geometry(geoset_chunks: List[str]) -> War3Geoset:
    print("parse_geometry")
    geoset = War3Geoset()
    geoset.name = ''

    matrix_indices = []
    matrix_groups_sizes = []
    vert_matrix_groups: List[int] = []
    matrix_groups: List[List[int]] = []

    locations: List[List[float]] = []
    normals: List[List[float]] = []
    uvs: List[List[float]] = []
    sw_bones: List[List[str]] = []
    sw_weights: List[List[int]] = []
    for data_chunk in geoset_chunks:
        label = data_chunk.split(" ", 1)[0]

        if label == "Vertices":
            vert_strings = chunkifier(extract_bracket_content(data_chunk))

            for vert in vert_strings:
                locations.append(extract_float_values(vert))

        if label == "Normals":
            norm_strings = chunkifier(extract_bracket_content(data_chunk))

            for norm in norm_strings:
                normals.append(extract_float_values(norm))

        if label == "Faces":
            triangles = chunkifier(extract_bracket_content(extract_bracket_content(data_chunk)))

            for triangle in triangles:
                triangle_values = extract_int_values(triangle)

                if len(triangle_values) == 3:
                    geoset.triangles.append(triangle_values)

                else:
                    for i in range(len(triangle_values)//3):
                        geoset.triangles.append(triangle_values[i*3:i*3+3])

        if label == "VertexGroup":
            vert_groups = extract_int_values(data_chunk)
            vert_matrix_groups = vert_groups

        if label == "Groups":
            matrices: List[str] = chunkifier(extract_bracket_content(data_chunk))

            for matrix in matrices:
                matrix_values: List[int] = extract_int_values(matrix)
                matrix_groups.append(matrix_values)

                matrix_groups_sizes.append(len(matrix_values))

                for value in matrix_values:
                    matrix_indices.append(value)

        if label == "TVertices":
            t_vertices = chunkifier(extract_bracket_content(data_chunk))

            for t_vertice in t_vertices:
                u, v = extract_float_values(t_vertice)
                uvs.append([u, 1 - v])

        if label == "SkinWeights":
            weights = chunkifier(extract_bracket_content(data_chunk))

            for weight in weights:
                sw_vals = extract_int_values(weight)
                sw_bones.append([str(s) for s in sw_vals[0:4]])
                sw_weights.append(sw_vals[4:8])

    # vert_bones: List[List[str]] = []
    # vert_weights: List[List[int]] = []
    if not len(sw_bones):
        for group in vert_matrix_groups:
            v_b: List[str] = []
            v_w: List[int] = []
            for bone in matrix_groups[group]:
                v_b.append(str(bone))
                v_w.append(255)
            sw_bones.append(v_b)
            sw_weights.append(v_w)

    for loc, norm, uv, v_b, v_w in zip(locations, normals, uvs, sw_bones, sw_weights):
        geoset.vertices.append(War3Vertex(loc, norm, uv, None, v_b, v_w))

    # vertex_groups, vertex_groups_ids = get_vertex_groups(vert_matrix_groups, matrix_groups_sizes, matrix_indices)
    # geoset.vertex_groups = vertex_groups
    # geoset.vertex_groups_ids = vertex_groups_ids
    geoset.matrices = sw_bones

    return geoset
