from ..classes.War3ImportBone import War3ImportBone
from .parse_node import parse_node


def parse_events(data, model):
    event = War3ImportBone()
    event.type = 'event'
    event.node = parse_node(data)
    model.nodes.append(event)
