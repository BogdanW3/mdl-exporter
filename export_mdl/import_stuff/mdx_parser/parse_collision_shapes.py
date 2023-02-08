from typing import List, Dict

from ...classes.War3CollisionShape import War3CollisionShape
from . import binary_reader
from .parse_node import parse_node
from ...classes.War3Node import War3Node


def parse_collision_shapes(data: bytes, id_to_node: Dict[str, War3Node]) -> List[War3CollisionShape]:
    data_size = len(data)
    r = binary_reader.Reader(data)

    nodes: List[War3CollisionShape] = []
    while r.offset < data_size:

        node = War3CollisionShape("")
        parse_node(r, node, id_to_node)
        collision_type = r.getf('<I')[0]

        if collision_type == 0:
            vertices_count = 2
            node.type = 'Box'
        elif collision_type == 1:
            vertices_count = 2
            node.type = 'Plane'
        elif collision_type == 2:
            vertices_count = 1
            node.type = 'Sphere'
        elif collision_type == 3:
            vertices_count = 2
            node.type = 'Cylinder'
        else:
            vertices_count = 1
            node.type = 'Sphere'
            print('UNSUPPORTED COLLISION SHAPE TYPE:', collision_type)
            # raise Exception('UNSUPPORTED COLLISION SHAPE TYPE:', collision_type)

        for _ in range(vertices_count):
            position = r.getf('<3f')
            node.verts.append(list(position))

        if collision_type == 2 or collision_type == 3:
            bounds_radius = r.getf('<f')[0]
            node.radius = bounds_radius

        nodes.append(node)
    return nodes
