from typing import List

from ...classes.War3Bone import War3Bone
from . import binary_reader
from .parse_node import parse_node


def parse_bones(data: bytes) -> List[War3Bone]:
    r = binary_reader.Reader(data)
    data_size = len(data)

    nodes: List[War3Bone] = []
    while r.offset < data_size:
        node = War3Bone("")
        parse_node(r, node)
        node.geoset_id = r.getf('<I')[0]
        geoset_animation_id = r.getf('<I')[0]
        nodes.append(node)
    return nodes
