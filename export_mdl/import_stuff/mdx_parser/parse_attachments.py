from typing import List, Dict

from . import binary_reader
from .parse_timeline import parse_timeline
from .parse_node import parse_node
from ... import constants
from ...classes.War3Attachment import War3Attachment
from ...classes.War3Node import War3Node


def parse_attachments(data: bytes) -> List[War3Attachment]:
    data_size = len(data)
    reader = binary_reader.Reader(data)

    nodes: List[War3Attachment] = []
    while reader.offset < data_size:
        inclusive_size = reader.getf('<I')[0]
        node_data_size = inclusive_size - 4
        node_data = data[reader.offset: reader.offset + node_data_size]
        reader.skip(node_data_size)

        r = binary_reader.Reader(node_data)
        data_size_chunk = len(node_data)
        node = War3Attachment("")
        parse_node(r, node)
        path = r.gets(260)
        node_id = r.getf('<I')[0]

        if r.offset < data_size_chunk:
            chunk_id = r.getid(constants.CHUNK_ATTACHMENT_VISIBILITY)
            visibility = parse_timeline(r, '<f')

        nodes.append(node)
    return nodes
