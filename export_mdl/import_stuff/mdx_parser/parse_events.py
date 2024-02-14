from typing import List

from ...classes.War3EventObject import War3EventObject
from ... import constants
from . import binary_reader
from .parse_node import parse_node
from .parse_tracks import parse_tracks


def parse_events(data: bytes) -> List[War3EventObject]:
    data_size = len(data)
    r = binary_reader.Reader(data)

    nodes: List[War3EventObject] = []
    while r.offset < data_size:

        node = War3EventObject("")
        parse_node(r, node)

        if r.offset < data_size:
            chunk_id = r.gets(4)

            if chunk_id == constants.CHUNK_EVENT_TRACKS:
                parse_tracks(r)
            else:
                r.offset -= 4

        nodes.append(node)
    return nodes
