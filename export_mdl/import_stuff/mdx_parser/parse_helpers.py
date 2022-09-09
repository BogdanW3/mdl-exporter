from typing import Union, List, Dict

from ...classes.War3Helper import War3Helper
from . import binary_reader
from .parse_node import parse_node
from ...classes.War3Node import War3Node


def parse_helpers(data: bytes, id_to_node: Dict[str, War3Node]) -> List[War3Helper]:
    data_size = len(data)
    r = binary_reader.Reader(data)

    nodes: List[War3Helper] = []
    while r.offset < data_size:
        helper = War3Helper("")
        parse_node(r, helper, id_to_node)
        nodes.append(helper)
    return nodes

