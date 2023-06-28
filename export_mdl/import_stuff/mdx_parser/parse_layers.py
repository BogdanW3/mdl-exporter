import struct

from ...classes.War3Layer import War3Layer
from ... import constants
from .binary_reader import Reader
from .parse_timeline import parse_timeline


def parse_layers(data: bytes, version: int) -> War3Layer:
    r = Reader(data)
    data_size = len(data)
    # print("layer data size: ", data_size)

    layer = War3Layer()
    # inclusive_size = r.offset + r.getf('<I')[0]
    layer.filter_mode = constants.FILTER_MODES.get(r.getf('<I')[0], 'None')
    layer.shadingFlags = r.getf('<I')[0]
    layer.texture_path = str(r.getf('<I')[0])
    layer.textureAnimationId = r.getf('<I')[0]
    layer.coordId = r.getf('<I')[0]
    layer.alpha_value = r.getf('<f')[0]
    # if constants.MDX_CURRENT_VERSION > 800:
    if 800 < version:
        layer.emissive_gain = r.getf('<f')[0]
        # if constants.MDX_CURRENT_VERSION > 900:

    if 900 < version:
        layer.fresnel_color = [r.getf('<f')[0], r.getf('<f')[0], r.getf('<f')[0]]
        layer.fresnel_opacity = r.getf('<f')[0]
        layer.fresnel_team_color = r.getf('<f')[0]

    if 1000 < version:
        hdFlag = r.getf('<I')[0]
        numTextures: int = r.getf('<I')[0]

        # print("numTextures:", numTextures)

        i = 0
        while i < numTextures:
            animOrTextureId = r.getf('<I')[0]
            # print("Texture:", i, ", animOrTextureId:", animOrTextureId)
            if 1024 < animOrTextureId:
                # print("animOrTexture:", animOrTextureId, "size: ", struct.calcsize('<I'))
                layer.texture_anim = parse_timeline(r, '<I')
                i -= 1
            else:
                textureSlot = r.getf('<I')[0]
                # print("textureSlot", textureSlot, "textureID: ", animOrTextureId)
            i += 1


    # print("r.offset:", r.offset)

    while r.offset < data_size:
        # print("r.offset:", r.offset)
        chunk_id = r.getid(constants.SUB_CHUNKS_LAYER)
        # print("layer chunk: " + chunk_id)
        if chunk_id == constants.CHUNK_MATERIAL_TEXTURE_ID:
            layer.texture_anim = parse_timeline(r, '<I')
        elif chunk_id == constants.CHUNK_MATERIAL_ALPHA:
            layer.alpha_anim = parse_timeline(r, '<f')
        elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_COLOR:
            layer.fresnel_color = parse_timeline(r, '<3f')
        elif chunk_id == constants.CHUNK_MATERIAL_EMISSIONS:
            layer.emissions = parse_timeline(r, '<f')
        elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_ALPHA:
            layer.fresnel_alpha = parse_timeline(r, '<f')
        elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_TEAMCOLOR:
            layer.fresnel_team_color = parse_timeline(r, '<f')

    return layer


def parse_layers(r: Reader, version: int) -> War3Layer:
    data_size = r.offset
    inclusive_size = r.getf('<I')[0]
    data_size = data_size + inclusive_size
    # print("inclusive_size: ", inclusive_size, "max offset: ", data_size)

    layer = War3Layer()
    # inclusive_size = r.offset + r.getf('<I')[0]
    layer.filter_mode = constants.FILTER_MODES.get(r.getf('<I')[0], 'None')
    layer.shadingFlags = r.getf('<I')[0]
    layer.texture_id = r.getf('<I')[0]
    layer.texture_path = str(layer.texture_id)
    layer.textureAnimationId = r.getf('<I')[0]
    layer.coordId = r.getf('<I')[0]
    layer.alpha_value = r.getf('<f')[0]

    if 800 < version:
        layer.emissive_gain = r.getf('<f')[0]

    if 900 < version:
        layer.fresnel_color = list(r.getf('<3f'))
        layer.fresnel_opacity = r.getf('<f')[0]
        layer.fresnel_team_color = r.getf('<f')[0]

    if 1000 < version:
        hdFlag = r.getf('<I')[0]
        numTextures: int = r.getf('<I')[0]

        # print("numTextures:", numTextures)

        i = 0
        while i < numTextures:
            animOrTextureId = r.getf('<I')[0]
            # print("Texture:", i, ", animOrTextureId:", animOrTextureId)
            if 1024 < animOrTextureId:
                i -= 1
                r.offset -= struct.calcsize('<I')
                anim_id = r.getid(constants.SUB_CHUNKS_LAYER)
                # print("Texture:", i, ", anim_id: ", anim_id)
                layer.texture_anim = parse_timeline(r, '<I')
            else:
                textureSlot = r.getf('<I')[0]
                # print("Texture:", i, "textureSlot", textureSlot, ", textureID: ", animOrTextureId)
            i += 1

    # print("r.offset:", r.offset, "of", data_size)

    while r.offset < data_size:
        chunk_id = r.getid(constants.SUB_CHUNKS_LAYER)
        # print("layer chunk: " + chunk_id)
        if chunk_id == constants.CHUNK_MATERIAL_TEXTURE_ID:
            layer.texture_anim = parse_timeline(r, '<I')
        elif chunk_id == constants.CHUNK_MATERIAL_ALPHA:
            layer.alpha_anim = parse_timeline(r, '<f')
        elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_COLOR:
            layer.fresnel_color = parse_timeline(r, '<3f')
        elif chunk_id == constants.CHUNK_MATERIAL_EMISSIONS:
            layer.emissions = parse_timeline(r, '<f')
        elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_ALPHA:
            layer.fresnel_alpha = parse_timeline(r, '<f')
        elif chunk_id == constants.CHUNK_MATERIAL_FRESNEL_TEAMCOLOR:
            layer.fresnel_team_color = parse_timeline(r, '<f')
        # print("r.offset:", r.offset, "of", data_size)

    return layer

