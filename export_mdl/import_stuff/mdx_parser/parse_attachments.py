from typing import List, Dict

from . import binary_reader
from .parse_alpha import parse_alpha
from .parse_node import parse_node
from ... import constants
from ...classes.War3Attachment import War3Attachment
from ...classes.War3Node import War3Node


def parse_attachments(data: bytes, id_to_node: Dict[str, War3Node]):
    data_size = len(data)
    r = binary_reader.Reader(data)

    nodes: List[War3Attachment] = []
    while r.offset < data_size:
        inclusive_size = r.getf('<I')[0]
        attach_data_size = inclusive_size - 4
        attach_data = data[r.offset: r.offset + attach_data_size]
        r.skip(attach_data_size)

        r = binary_reader.Reader(attach_data)
        data_size = len(attach_data)
        attachment = War3Attachment("")
        parse_node(r, attachment, id_to_node)
        path = r.gets(260)
        attachment_id = r.getf('<I')[0]

        if r.offset < data_size:
            chunk_id = r.getid(constants.CHUNK_ATTACHMENT_VISIBILITY)
            visibility = parse_alpha(r)

        nodes.append(attachment)
    return nodes
