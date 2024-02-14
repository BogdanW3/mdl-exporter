from .parse_node import parse_node
from ...classes.War3Helper import War3Helper


def parse_helpers(data: str) -> War3Helper:
    helper = War3Helper("")
    parse_node(data, helper)

    return helper
