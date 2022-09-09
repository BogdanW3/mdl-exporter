from typing import Dict

from .binary_reader import Reader
from ...classes.War3Node import War3Node
from ... import constants
from .parse_geoset_transformation import parse_geoset_transformation


def parse_node(r: Reader, node: War3Node, id_to_node: Dict[str, War3Node]):
    inclusive_size = r.offset + r.getf('<I')[0]
    node.name = r.gets(80)
    node_id = r.getf('<I')[0]
    id_to_node[str(node_id)] = node
    parent = r.getf('<I')[0]

    if parent != 0xffffffff:
        node.parent = str(parent)
    # if parent == 0xffffffff:
    #     node.parent = None

    flags = r.getf('<I')[0]

    while r.offset < inclusive_size:
        chunk_id = r.getid(constants.SUB_CHUNKS_NODE)

        if chunk_id == constants.CHUNK_GEOSET_TRANSLATION:
            node.anim_loc = parse_geoset_transformation(r, '<3f')
        elif chunk_id == constants.CHUNK_GEOSET_ROTATION:
            node.anim_rot = parse_geoset_transformation(r, '<4f')
        elif chunk_id == constants.CHUNK_GEOSET_SCALING:
            node.anim_scale = parse_geoset_transformation(r, '<3f')

    return node
