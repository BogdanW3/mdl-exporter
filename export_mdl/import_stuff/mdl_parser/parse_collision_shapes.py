from typing import Dict

from .parse_node import parse_node
from ...classes.War3CollisionShape import War3CollisionShape
from ...classes.War3Node import War3Node


def parse_collision_shapes(data: str, id_to_node: Dict[str, War3Node]) -> War3CollisionShape:
    collision_shape = War3CollisionShape("")
    parse_node(data, collision_shape, id_to_node)
    return collision_shape
