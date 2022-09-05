from typing import Dict

from .parse_node import parse_node
from ...classes.War3EventObject import War3EventObject
from ...classes.War3Node import War3Node


def parse_events(data: str, id_to_node: Dict[str, War3Node]) -> War3EventObject:
    event = War3EventObject("")
    parse_node(data, event, id_to_node)
    return event
