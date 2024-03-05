from typing import List

from .mdl_reader import chunkifier, extract_bracket_content, extract_float_values, extract_int_values
from ... import mdl_constants

from ...classes.War3Geoset import War3Geoset
from ...classes.War3Vertex import War3Vertex


def parse_geometry(geoset_chunks: List[str]) -> War3Geoset:
    print("parse_geometry")
    geoset = War3Geoset()
    geoset.name = ''

    matrix_node_ids: List[int] = []
    matrix_groups_sizes: List[int] = []
    vert_matrix_groups: List[int] = []
    matrix_groups: List[List[int]] = []

    locations: List[List[float]] = []
    normals: List[List[float]] = []
    uvs: List[List[float]] = []
    sw_bones: List[List[str]] = []
    sw_weights: List[List[int]] = []
    for data_chunk in geoset_chunks:
        label = data_chunk.split(" ", 1)[0]

        if label == mdl_constants.VERTICES:
            # print("parsing verts")
            vert_strings = chunkifier(extract_bracket_content(data_chunk))
            # print("found %s lines with verts" % len(vert_strings))
            for vert in vert_strings:
                values = extract_float_values(vert)
                locations.append(values)

        if label == mdl_constants.NORMALS:
            norm_strings = chunkifier(extract_bracket_content(data_chunk))

            for norm in norm_strings:
                normals.append(extract_float_values(norm))

        if label == mdl_constants.FACES:
            triangles = chunkifier(extract_bracket_content(extract_bracket_content(data_chunk)))

            for triangle in triangles:
                triangle_values = extract_int_values(triangle)

                if len(triangle_values) == 3:
                    geoset.triangles.append(triangle_values)
                else:
                    for i in range(len(triangle_values)//3):
                        geoset.triangles.append(triangle_values[i*3:i*3+3])

        if label == mdl_constants.VERTEX_GROUP:
            vert_groups = extract_int_values(data_chunk)
            vert_matrix_groups = vert_groups

        if label == mdl_constants.GROUPS:
            matrices: List[str] = chunkifier(extract_bracket_content(data_chunk))

            for matrix in matrices:
                matrix_values: List[int] = extract_int_values(matrix)
                matrix_groups.append(matrix_values)

                matrix_groups_sizes.append(len(matrix_values))

                for matrix_node_id in matrix_values:
                    matrix_node_ids.append(matrix_node_id)

        if label == mdl_constants.T_VERTICES:
            t_vertices = chunkifier(extract_bracket_content(data_chunk))

            for t_vertex in t_vertices:
                u, v = extract_float_values(t_vertex)
                uvs.append([u, 1 - v])

        if label == mdl_constants.SKIN_WEIGHTS:
            # print("parsing SkinWeights")
            # print(data_chunk)
            if data_chunk.count("{") < 1:
                skinning = chunkifier(data_chunk)
            else:
                content = extract_bracket_content(data_chunk)
                skinning = content.split("\n")
                # print(skinning)
            # print("found %s lines with SkinWeights" % len(skinning))

            for bones_weights in skinning:
                sw_vals = extract_int_values(bones_weights)
                sw_bones.append([str(s) for s in sw_vals[0:4]])
                sw_weights.append(sw_vals[4:8])

    if not len(sw_bones):
        for group in vert_matrix_groups:
            v_b: List[str] = []
            v_w: List[int] = []
            for bone in matrix_groups[group]:
                v_b.append(str(bone))
                v_w.append(255)
            sw_bones.append(v_b)
            sw_weights.append(v_w)

    # print("locations:", len(locations), "normals:", len(normals), "uvs:", len(uvs), "sw_bones:", len(sw_bones), "sw_weights:", len(sw_weights), )
    for loc, norm, uv, v_b, v_w in zip(locations, normals, uvs, sw_bones, sw_weights):
        # print("\t adding vert to geoset ", loc, "weight:", v_w, "bone:", v_b)
        geoset.vertices.append(War3Vertex(loc, norm, uv, v_b, v_w))

    geoset.matrices = sw_bones

    return geoset
