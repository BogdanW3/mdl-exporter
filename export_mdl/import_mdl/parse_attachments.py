from ..classes.War3ImportBone import War3ImportBone
from .parse_node import parse_node


def parse_attachments(data, model):
    attachment = War3ImportBone()
    attachment.type = 'attachment'
    attachment.node = parse_node(data)
    model.nodes.append(attachment)
