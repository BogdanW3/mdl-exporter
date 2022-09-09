from typing import List

from ...classes.War3Material import War3Material
from . import binary_reader
from .parse_layers import parse_layers


def parse_materials(data: bytes, version: int) -> List[War3Material]:
    r = binary_reader.Reader(data)
    data_size = len(data)

    materials: List[War3Material] = []

    while r.offset < data_size:
        material = War3Material("")
        inclusive_size = r.getf('<I')[0]
        priority_plane = r.getf('<I')[0]
        flags = r.getf('<I')[0]

        # if constants.MDX_CURRENT_VERSION > 800:
        if version > 800:
            shader = r.gets(80)
            if shader == "Shader_HD_DefaultUnit":
                material.hd = True
            layer_chunk_data_size = inclusive_size - 92
        else:
            layer_chunk_data_size = inclusive_size - 12

        if layer_chunk_data_size > 0:
            layer_chunk_data: bytes = data[r.offset: r.offset + layer_chunk_data_size]
            r.skip(layer_chunk_data_size)
            material.layers = parse_layers(layer_chunk_data, version)

        materials.append(material)
    return materials
