from typing import Dict

from .parse_node import parse_node
from ...classes.War3Helper import War3Helper
from ...classes.War3Node import War3Node


def parse_helpers(data: str, id_to_node: Dict[str, War3Node]) -> War3Helper:
    helper = War3Helper("")
    parse_node(data, helper, id_to_node)

    return helper
