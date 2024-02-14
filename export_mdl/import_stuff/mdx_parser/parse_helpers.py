from typing import List

from ...classes.War3Helper import War3Helper
from . import binary_reader
from .parse_node import parse_node


def parse_helpers(data: bytes) -> List[War3Helper]:
    data_size = len(data)
    r = binary_reader.Reader(data)

    nodes: List[War3Helper] = []
    while r.offset < data_size:
        node = War3Helper("")
        parse_node(r, node)
        nodes.append(node)
    return nodes

