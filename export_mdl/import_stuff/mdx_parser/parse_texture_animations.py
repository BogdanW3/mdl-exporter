from typing import List

from ... import constants
from ...classes.War3TextureAnim import War3TextureAnim
from .binary_reader import Reader
from .parse_timeline import parse_timeline


def parse_texture_animations(data: bytes) -> List[War3TextureAnim]:
    """TXAN: per entry an inclusive size, then optional translation (KTAT), rotation (KTAR, a quaternion) and
    scaling (KTAS) tracks, applied to the UVs of the layers that refer to it."""
    r = Reader(data)
    data_size = len(data)
    anims: List[War3TextureAnim] = []
    while r.offset < data_size:
        start = r.offset
        size = r.getf('<I')[0]
        end = start + size
        anim = War3TextureAnim()
        while r.offset < end:
            chunk_id = r.getid((constants.CHUNK_TEX_ANIM_TRANSLATION, constants.CHUNK_TEX_ANIM_ROTATION,
                                constants.CHUNK_TEX_ANIM_SCALING))
            if chunk_id == constants.CHUNK_TEX_ANIM_TRANSLATION:
                anim.translation = parse_timeline(r, '<3f')
                anim.translation.type = 'Translation'
            elif chunk_id == constants.CHUNK_TEX_ANIM_ROTATION:
                anim.rotation = parse_timeline(r, '<4f')
                anim.rotation.type = 'Rotation'
            elif chunk_id == constants.CHUNK_TEX_ANIM_SCALING:
                anim.scale = parse_timeline(r, '<3f')
                anim.scale.type = 'Scale'
        r.offset = end
        anims.append(anim)
    return anims
