from typing import List, Dict

from ...classes.War3Light import War3Light
from . import binary_reader
from .parse_node import parse_node
from ...classes.War3Node import War3Node


def parse_lights(data: bytes, id_to_node: Dict[str, War3Node]) -> List[War3Light]:
    data_size = len(data)
    r = binary_reader.Reader(data)

    nodes: List[War3Light] = []
    while r.offset < data_size:
        helper = War3Light("")
        parse_node(r, helper, id_to_node)
        nodes.append(helper)
    return nodes

