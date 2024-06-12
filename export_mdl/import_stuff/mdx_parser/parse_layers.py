import struct

from ...classes.War3Layer import War3Layer
from ... import constants
from .binary_reader import Reader
from .parse_timeline import parse_timeline

def parse_layers(r: Reader, version: int) -> War3Layer:
    data_size = r.offset
    inclusive_size = r.getf('<I')[0]
    data_size = data_size + inclusive_size

    layer = War3Layer()
    layer.filter_mode = constants.FILTER_MODES.get(r.getf('<I')[0], 'None')
    shadingFlags = r.getf('<I')[0]
    if shadingFlags & 0x1:
        layer.unshaded = True
    if shadingFlags & 0x2:
        # sphere env map
        pass
    if shadingFlags & 0x4:
        # unknown
        pass
    if shadingFlags & 0x8:
        # unknown
        pass
    if shadingFlags & 0x10:
        layer.two_sided = True
    if shadingFlags & 0x20:
        layer.unfogged = True
    if shadingFlags & 0x40:
        layer.no_depth_test = True
    if shadingFlags & 0x80:
        layer.no_depth_set = True

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
        layer.hd = r.getf('<I')[0]
        numTextures: int = r.getf('<I')[0]

        # print("numTextures:", numTextures)

        layer.multi_texture_ids = []
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
                layer.multi_texture_ids.append(animOrTextureId)
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