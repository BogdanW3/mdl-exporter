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
    layer.unshaded = bool(shadingFlags & 0x1)
    layer.sphere_env_map = bool(shadingFlags & 0x2)
    layer.wrap_width = bool(shadingFlags & 0x4)
    layer.wrap_height = bool(shadingFlags & 0x8)
    layer.two_sided = bool(shadingFlags & 0x10)
    layer.unfogged = bool(shadingFlags & 0x20)
    layer.no_depth_test = bool(shadingFlags & 0x40)
    layer.no_depth_set = bool(shadingFlags & 0x80)
    layer.unlit = bool(shadingFlags & 0x100)
    layer.back_faces_for_shadows = bool(shadingFlags & 0x200)
    layer.ambient_occlusion = bool(shadingFlags & 0x400)

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
        layer.shader = r.getf('<I')[0]
        layer.hd = layer.shader in constants.HD_SHADER_IDS
        numTextures: int = r.getf('<I')[0]

        # Each texture is an id and a PBR slot, optionally followed by its own KMTF flipbook track
        layer.multi_texture_ids = []
        for _ in range(numTextures):
            texture_id, texture_slot = r.getf('<2I')
            layer.multi_texture_ids.append(texture_id)
            if r.peek_id() == constants.CHUNK_MATERIAL_TEXTURE_ID:
                r.skip(4)
                layer.texture_anim = parse_timeline(r, '<I')

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
        else:
            # An unknown track can't be skipped without knowing its value size, give up on the rest of the layer
            r.offset = data_size

    return layer
