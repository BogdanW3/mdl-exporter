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
        priority_plane = r.getf('<I')[0]
        flags = r.getf('<I')[0]
        # print("material size: ", inclusive_size, ", priority_plane:", priority_plane, ", flags:", flags)

        layer_chunk_data_size = inclusive_size - 12
        # if constants.MDX_CURRENT_VERSION > 800:
        if 800 < version < 1100:
            shader = r.gets(80)
            if shader == "Shader_HD_DefaultUnit":
                material.is_hd = True
            # print("Shader: " + shader)
            layer_chunk_data_size = layer_chunk_data_size - 80

        if 0 < layer_chunk_data_size:
            chunk_id = r.getid(constants.CHUNK_LAYER)
            layers_count = r.getf('<I')[0]
            # print("layer chunkId:", chunk_id, ", count:", layers_count)

            for _ in range(layers_count):
                layer = parse_layers(r, version)
                if layer.multi_texture_ids:
                    material.is_hd = 1000 <= version
                    for texture_id in layer.multi_texture_ids:
                        newLayer = War3Layer()
                        newLayer.texture_id = layer.multi_texture_ids[texture_id]
                        newLayer.texture_path = layer.texture_path
                        newLayer.texture = layer.texture
                        newLayer.filter_mode = layer.filter_mode
                        newLayer.unshaded = layer.unshaded
                        newLayer.two_sided = layer.two_sided
                        newLayer.unfogged = layer.unfogged
                        newLayer.texture_anim = layer.texture_anim
                        newLayer.alpha_anim = layer.alpha_anim
                        newLayer.alpha_value = layer.alpha_value
                        newLayer.no_depth_test = layer.no_depth_test
                        newLayer.no_depth_set = layer.no_depth_set
                        material.layers.append(newLayer)
                else:
                    material.layers.append(layer)

        materials.append(material)
    return materials
