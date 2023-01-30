from typing import List

from ...classes.War3GeosetAnim import War3GeosetAnim
from ... import constants
from . import binary_reader
from .parse_timeline import parse_timeline


def parse_geoset_animations(data: bytes):
    r = binary_reader.Reader(data)
    data_size = len(data)

    geoset_animations: List[War3GeosetAnim] = []
    while r.offset < data_size:
        inclusive_size = r.offset + r.getf('<I')[0]
        alpha = list(r.getf('<f'))
        flags = r.getf('<I')[0]
        color = list(r.getf('<3f'))
        geoset_id = r.getf('<I')[0]
        animation_color = None
        animation_alpha = None
        while r.offset < inclusive_size:
            chunk_id = r.getid(constants.SUB_CHUNKS_GEOSET_ANIMATION)

            if chunk_id == constants.CHUNK_GEOSET_COLOR:
                animation_color = parse_timeline(r, '<3f')
            elif chunk_id == constants.CHUNK_GEOSET_ALPHA:
                animation_alpha = parse_timeline(r, '<f')

        geoset_animation = War3GeosetAnim(color, alpha, animation_color, animation_alpha)
        geoset_animation.geoset_id = geoset_id
        geoset_animations.append(geoset_animation)
    return geoset_animations
