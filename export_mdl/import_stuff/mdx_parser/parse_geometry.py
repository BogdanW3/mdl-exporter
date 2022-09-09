from typing import List

from ...classes.War3Geoset import War3Geoset
from ...classes.War3Vertex import War3Vertex
from .binary_reader import Reader
from ... import constants
from .get_vertex_groups import get_vertex_groups


def parse_geometry(data: bytes, version: int) -> War3Geoset:
    r = Reader(data)
    geoset = War3Geoset()
    geoset.name = ''

    # parse vertices
    chunk_id = r.getid(constants.CHUNK_VERTEX_POSITION)
    print(chunk_id)
    vertex_count = r.getf('<I')[0]
    print(vertex_count)
    locations: List[List[float]] = []
    for _ in range(vertex_count):
        vertex_position = list(r.getf('<3f'))
        locations.append(vertex_position)

    # parse normals
    chunk_id = r.getid(constants.CHUNK_VERTEX_NORMAL)
    print(chunk_id)
    normal_count = r.getf('<I')[0]
    print(normal_count)
    normals: List[List[float]] = []
    for _ in range(normal_count):
        normal = list(r.getf('<3f'))
        normals.append(normal)

    # Read and ignore
    # chunks_to_skip = [[constants.CHUNK_VERTEX_NORMAL, '<3f'], [constants.CHUNK_FACE_TYPE_GROUP, '<I'], [constants.CHUNK_FACE_GROUP, '<I']]
    chunks_to_skip = [[constants.CHUNK_FACE_TYPE_GROUP, '<I'], [constants.CHUNK_FACE_GROUP, '<I']]
    for chunk in chunks_to_skip:
        chunk_id = r.getid(chunk[0])
        count = r.getf('<I')[0]

        for _ in range(count):
            chunk_thing = r.getf(chunk[1])

    # parse
    chunk_id = r.getid(constants.CHUNK_FACE)
    indices_count = r.getf('<I')[0]

    if indices_count % 3 != 0:
        raise Exception('bad indices (indices_count % 3 != 0)')

    for _ in range(indices_count // 3):
        triangle: List[int] = list(r.getf('<3H'))
        geoset.triangles.append(triangle)

    matrix_indices: List[int] = []
    matrix_groups_sizes: List[int] = []
    vert_matrix_groups: List[int] = []
    matrix_groups: List[List[int]] = []
    sw_bones: List[List[str]] = []
    sw_weights: List[List[int]] = []

    # parse vertex groups
    chunk_id = r.getid(constants.CHUNK_VERTEX_GROUP)
    matrix_groups_count = r.getf('<I')[0]
    for _ in range(matrix_groups_count):
        matrix_group = r.getf('<B')[0]
        vert_matrix_groups.append(matrix_group)

    # parse matrix Groups
    chunk_id = r.getid(constants.CHUNK_MATRIX_GROUP)
    matrix_groups_sizes_count = r.getf('<I')[0]
    for _ in range(matrix_groups_sizes_count):
        matrix_group_size = r.getf('<I')[0]
        matrix_groups_sizes.append(matrix_group_size)

    # parse MatrixIndices
    chunk_id = r.getid(constants.CHUNK_MATRIX_INDEX)
    matrix_indices_count = r.getf('<I')[0]
    for _ in range(matrix_indices_count):
        matrix_index = r.getf('<I')[0]
        matrix_indices.append(matrix_index)

    curr_index = 0
    for size in matrix_groups_sizes:
        matrix_values: List[int] = []
        for m_i in matrix_indices[curr_index: curr_index+size]:
            matrix_values.append(m_i)
        curr_index += len(matrix_values)
        matrix_groups.append(matrix_values)

    # parse geoset material
    geoset.mat_name = str(r.getf('<I')[0])

    selection_group = r.getf('<I')[0]
    selection_flags = r.getf('<I')[0]

    # if constants.MDX_CURRENT_VERSION > 800:
    if version > 800:
        lod = r.getf('<I')[0]
        lod_name = r.gets(80)

    # parse geoset extents
    bounds_radius = r.getf('<f')[0]
    minimum_extent = r.getf('<3f')
    maximum_extent = r.getf('<3f')

    extents_count = r.getf('<I')[0]
    for _ in range(extents_count):
        bounds_radius = r.getf('<f')[0]
        minimum_extent = r.getf('<3f')
        maximum_extent = r.getf('<3f')

    # if constants.MDX_CURRENT_VERSION > 800:
    if version > 800:
        chunk_id = r.getid((constants.CHUNK_TANGENTS, constants.CHUNK_SKIN, constants.CHUNK_TEXTURE_VERTEX_GROUP))
        if chunk_id == constants.CHUNK_TANGENTS:
            tangent_size = r.getf('<I')[0]
            r.skip(16 * tangent_size)
            chunk_id = r.getid((constants.CHUNK_SKIN, constants.CHUNK_TEXTURE_VERTEX_GROUP))
        if chunk_id == constants.CHUNK_SKIN:
            skin_size = r.getf('<I')[0]
            for i in range(skin_size // 8):
                sw_weight = r.getf('<8B')
                sw_bones.append([str(sw_weight[0]), str(sw_weight[1]), str(sw_weight[2]), str(sw_weight[3])])
                sw_weights.append([sw_weight[4], sw_weight[5], sw_weight[6], sw_weight[7]])
            r.skip(skin_size % 8)
            chunk_id = r.getid(constants.CHUNK_TEXTURE_VERTEX_GROUP)
    else:
        chunk_id = r.getid(constants.CHUNK_TEXTURE_VERTEX_GROUP)
    texture_vertex_group_count = r.getf('<I')[0]

    # parse uv-coordinates
    chunk_id = r.getid(constants.CHUNK_VERTEX_TEXTURE_POSITION)
    vertex_texture_position_count = r.getf('<I')[0]

    uvs: List[List[float]] = []
    for _ in range(vertex_texture_position_count):
        u, v = r.getf('<2f')
        uvs.append([u, 1 - v])

    if not len(sw_bones):
        for group in vert_matrix_groups:
            v_b: List[str] = []
            v_w: List[int] = []
            for bone in matrix_groups[group]:
                v_b.append(str(bone))
                v_w.append(255)
            sw_bones.append(v_b)
            sw_weights.append(v_w)

    for pos, norm, uv, v_b, v_w in zip(locations, normals, uvs, sw_bones, sw_weights):
        geoset.vertices.append(War3Vertex(pos, norm, uv, None, v_b, v_w))

    geoset.matrices = sw_bones

    return geoset
