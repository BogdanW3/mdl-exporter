from typing import Dict

from .parse_node import parse_node
from .mdl_reader import get_between, extract_bracket_content, chunkifier
from ...classes.War3Attachment import War3Attachment
from ...classes.War3Node import War3Node


def parse_attachments(data: str, id_to_node: Dict[str, War3Node]) -> War3Attachment:
    attachment = War3Attachment("")
    parse_node(data, attachment, id_to_node)

    if data.find("AttachmentID") > -1:
        attachment.attachment_id = int(get_between(data, "AttachmentID", ","))

    # if data.find("AttachmentID") > -1:
    #     attachment.attachment_id = int(get_between(data, "AttachmentID", ","))
    return attachment
