from typing import List, Dict

from ...classes.War3Bone import War3Bone
from . import binary_reader
from .parse_node import parse_node
from ...classes.War3Node import War3Node


def parse_bones(data: bytes, id_to_node: Dict[str, War3Node]) -> List[War3Bone]:
    r = binary_reader.Reader(data)
    data_size = len(data)

    nodes: List[War3Bone] = []
    while r.offset < data_size:
        node = War3Bone("")
        parse_node(r, node, id_to_node)
        node.geoset_id = r.getf('<I')[0]
        geoset_animation_id = r.getf('<I')[0]
        nodes.append(node)
    return nodes
