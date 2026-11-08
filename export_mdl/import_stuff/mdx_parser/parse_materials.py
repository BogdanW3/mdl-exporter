import copy
from typing import List

from ... import constants
from ...classes.War3Layer import War3Layer
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
        priority_plane = r.getf('<i')[0]
        flags = r.getf('<I')[0]
        material.priority_plane = priority_plane
        material.use_const_color = bool(flags & 0x1)
        hd_override = False
        shader_id = 0
        # print("material size: ", inclusive_size, ", priority_plane:", priority_plane, ", flags:", flags)

        layer_chunk_data_size = inclusive_size - 12
        if 800 < version < 1100:
            shader_id = constants.shader_id_from_name(r.gets(80))
            hd_override = shader_id in constants.HD_SHADER_IDS
            layer_chunk_data_size = layer_chunk_data_size - 80

        if 0 < layer_chunk_data_size:
            r.getid(constants.CHUNK_LAYER)
            layers_count = r.getf('<I')[0]
            # print("layer chunkId:", chunk_id, ", count:", layers_count)

            for _ in range(layers_count):
                layer = parse_layers(r, version)
                if layer.multi_texture_ids:
                    # v1100+ keeps all PBR textures in one layer, split them like the pre-v1100 HD layout
                    for texture_id in layer.multi_texture_ids:
                        newLayer = copy.copy(layer)
                        newLayer.multi_texture_ids = None
                        newLayer.texture_id = texture_id
                        newLayer.texture_path = str(newLayer.texture_id)
                        material.layers.append(newLayer)
                else:
                    if hd_override:
                        layer.hd = True
                        layer.shader = shader_id
                    material.layers.append(layer)

        materials.append(material)
    return materials
