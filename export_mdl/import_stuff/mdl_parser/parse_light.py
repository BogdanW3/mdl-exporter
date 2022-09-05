from typing import Dict

from .parse_node import parse_node
from ...classes.War3Light import War3Light
from ...classes.War3Node import War3Node


def parse_light(data: str, id_to_node: Dict[str, War3Node]) -> War3Light:
    light = War3Light("")
    parse_node(data, light, id_to_node)

    return light
