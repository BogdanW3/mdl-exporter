from ..classes.War3ImportBone import War3ImportBone
from .parse_node import parse_node


def parse_collision_shapes(data, model):
    collisionShape = War3ImportBone()
    collisionShape.type = 'collision_shape'
    collisionShape.node = parse_node(data)
    model.nodes.append(collisionShape)
