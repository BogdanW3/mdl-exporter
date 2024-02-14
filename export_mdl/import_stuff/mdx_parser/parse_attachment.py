from ... import constants
from ...classes.War3Attachment import War3Attachment
from . import binary_reader
from .parse_timeline import parse_timeline
from .parse_node import parse_node


def parse_attachment(attach_data: bytes) -> War3Attachment:
    r = binary_reader.Reader(attach_data)
    data_size = len(attach_data)
    node = War3Attachment("")
    parse_node(r, node)
    path = r.gets(260)
    node_id = r.getf('<I')[0]

    if r.offset < data_size:
        chunk_id = r.getid(constants.CHUNK_ATTACHMENT_VISIBILITY)
        visibility = parse_timeline(r, '<f')
    return node
