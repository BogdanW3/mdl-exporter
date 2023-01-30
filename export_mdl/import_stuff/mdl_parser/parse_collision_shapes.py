from typing import Dict

from .mdl_reader import get_between, chunkifier, extract_bracket_content, extract_float_values
from .parse_node import parse_node
from ...classes.War3CollisionShape import War3CollisionShape
from ...classes.War3Node import War3Node


def parse_collision_shapes(data: str, id_to_node: Dict[str, War3Node]) -> War3CollisionShape:
    collision_shape = War3CollisionShape("")
    if data.find("BoundsRadius") > -1:
        collision_shape.radius = float(get_between(data, "BoundsRadius", ","))

    if data.find("Vertices") > -1:
        vert_data = data.split("Vertices")[1]
        verts_string = extract_bracket_content(vert_data)
        vert_strings = chunkifier(verts_string)
        for string in vert_strings:
            line_values = extract_float_values(string)
            collision_shape.verts.append(line_values)

    if data.find("Sphere") > -1:
        collision_shape.type = "Sphere"
    elif data.find("Box") > -1:
        collision_shape.type = "Box"
    elif data.find("Plane") > -1:
        collision_shape.type = "Plane"
    elif data.find("Cylinder") > -1:
        collision_shape.type = "Cylinder"
    parse_node(data, collision_shape, id_to_node)
    return collision_shape
