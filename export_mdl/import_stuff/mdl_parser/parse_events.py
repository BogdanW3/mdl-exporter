from .parse_node import parse_node
from ...classes.War3EventObject import War3EventObject


def parse_events(data: str) -> War3EventObject:
    event = War3EventObject("")
    parse_node(data, event)
    return event
