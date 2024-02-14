from typing import Dict

from .parse_node import parse_node
from .mdl_reader import get_between
from ...classes.War3Attachment import War3Attachment
from ...classes.War3Node import War3Node


def parse_attachments(data: str) -> War3Attachment:
    attachment = War3Attachment("")
    parse_node(data, attachment)

    if -1 < data.find("AttachmentID"):
        attachment.attachment_id = int(get_between(data, "AttachmentID", ","))

    return attachment
