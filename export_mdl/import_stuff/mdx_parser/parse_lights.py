from typing import List, Dict

from ...classes.War3Light import War3Light
from . import binary_reader
from .parse_node import parse_node
from ...classes.War3Node import War3Node


def parse_lights(data: bytes, id_to_node: Dict[str, War3Node]) -> List[War3Light]:
    data_size = len(data)
    reader = binary_reader.Reader(data)

    nodes: List[War3Light] = []
    while reader.offset < data_size:
        inclusive_size = reader.getf('<I')[0]
        node_data_size = inclusive_size - 4
        node_data = data[reader.offset: reader.offset + node_data_size]
        reader.skip(node_data_size)

        r = binary_reader.Reader(node_data)
        data_size_chunk = len(node_data)
        node = War3Light("")
        parse_node(r, node, id_to_node)
        nodes.append(node)
    return nodes

