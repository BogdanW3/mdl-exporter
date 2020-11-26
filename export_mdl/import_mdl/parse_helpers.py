from ..classes.War3ImportBone import War3ImportBone
from .parse_node import parse_node


def parse_helpers(data, model):
    helper = War3ImportBone()
    helper.type = 'helper'
    helper.node = parse_node(data)

    model.nodes.append(helper)
