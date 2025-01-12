from .binary_reader import Reader
from ...classes.War3Node import War3Node
from ... import constants
from .parse_timeline import parse_timeline


def parse_node(r: Reader, node: War3Node):
    inclusive_size = r.offset + r.getf('<I')[0]
    node.name = r.gets(80)
    node_id = r.getf('<I')[0]
    node.obj_id = int(node_id)
    parent = r.getf('<I')[0]

    if parent != 0xffffffff:
        node.parent_id = parent
        node.parent = str(parent)

    flags = r.getf('<I')[0]

    while r.offset < inclusive_size:
        chunk_id = r.getid(constants.SUB_CHUNKS_NODE)

        if chunk_id == constants.CHUNK_GEOSET_TRANSLATION:
            node.anim_loc = parse_timeline(r, '<3f')
        elif chunk_id == constants.CHUNK_GEOSET_ROTATION:
            node.anim_rot = parse_timeline(r, '<4f')
        elif chunk_id == constants.CHUNK_GEOSET_SCALING:
            node.anim_scale = parse_timeline(r, '<3f')

    return node
