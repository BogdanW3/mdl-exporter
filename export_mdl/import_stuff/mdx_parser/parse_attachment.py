from typing import Dict

from ... import constants
from ...classes import War3Node
from ...classes.War3Attachment import War3Attachment
from . import binary_reader
from .parse_alpha import parse_alpha
from .parse_node import parse_node


def parse_attachment(attach_data: bytes, id_to_node: Dict[str, War3Node]):
    r = binary_reader.Reader(attach_data)
    data_size = len(attach_data)
    attachment = War3Attachment("")
    parse_node(r, attachment, id_to_node)
    path = r.gets(260)
    attachment_id = r.getf('<I')[0]

    if r.offset < data_size:
        chunk_id = r.getid(constants.CHUNK_ATTACHMENT_VISIBILITY)
        visibility = parse_alpha(r)
    return attachment
