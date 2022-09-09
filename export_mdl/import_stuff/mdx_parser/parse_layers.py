from typing import List

from ...classes.War3Layer import War3Layer
from ... import constants
from . import binary_reader
from .parse_alpha import parse_alpha
from .parse_material_texture_id import parse_material_texture_id
from .parse_fresnel_color import parse_fresnel_color


def parse_layers(data: bytes, version: int) -> List[War3Layer]:
    r = binary_reader.Reader(data)
    chunk_id = r.getid(constants.CHUNK_LAYER)
    layers_count = r.getf('<I')[0]
    layers = []

    for _ in range(layers_count):
        layer = War3Layer()
        inclusive_size = r.offset + r.getf('<I')[0]
        layer.filter_mode = constants.FILTER_MODES.get(r.getf('<I')[0], 'None')
        layer.shadingFlags = r.getf('<I')[0]
        layer.texture_path = str(r.getf('<I')[0])
        layer.textureAnimationId = r.getf('<I')[0]
        layer.coordId = r.getf('<I')[0]
        layer.alpha_value = r.getf('<f')[0]
        # if constants.MDX_CURRENT_VERSION > 800:
        if version > 800:
            layer.emissive_gain = r.getf('<f')[0]
            # if constants.MDX_CURRENT_VERSION > 900:
            if version > 900:
                layer.fresnel_color = [r.getf('<f')[0], r.getf('<f')[0], r.getf('<f')[0]]
                layer.fresnel_opacity = r.getf('<f')[0]
                layer.fresnel_team_color = r.getf('<f')[0]
        while r.offset < inclusive_size:
            chunk_id = r.getid(constants.SUB_CHUNKS_LAYER)
            if chunk_id == constants.CHUNK_MATERIAL_TEXTURE_ID:
                layer.texture_anim = parse_material_texture_id(r)
            elif chunk_id == constants.CHUNK_MATERIAL_ALPHA:
                layer.alpha_anim = parse_alpha(r)
            elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_COLOR:
                layer.fresnel_color = parse_fresnel_color(r)
            elif chunk_id == constants.CHUNK_MATERIAL_EMISSIONS:
                layer.emissions = parse_alpha(r)
            elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_ALPHA:
                layer.fresnel_alpha = parse_alpha(r)
            elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_TEAMCOLOR:
                layer.fresnel_team_color = parse_alpha(r)
        layers.append(layer)

    return layers
