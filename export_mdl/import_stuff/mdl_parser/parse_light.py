from .parse_node import parse_node
from ...classes.War3Light import War3Light


def parse_light(data: str) -> War3Light:
    light = War3Light("")
    parse_node(data, light)

    return light
