import re
from typing import Dict

from .parse_geoset_transformation import parse_geoset_transformation
from .mdl_reader import get_between, extract_bracket_content, chunkifier
from ...classes.War3Node import War3Node


def parse_node(data: str, node: War3Node, id_to_node: Dict[str, War3Node]):
    # print("parse_node")
    node.name = data.split("\"")[1]
    node.id = 0
    if data.find("ObjectId") > -1:
        # node.id = int(get_between(data, "ObjectId", ","))
        id_to_node[get_between(data, "ObjectId", ",")] = node

    node.parent = None
    if data.find("Parent") > -1:
        node.parent = get_between(data, "Parent", ",")

    # if data.find("AttachmentID") > -1:
    #     node.attachment_id = int(get_between(data, "AttachmentID", ","))

    bone_info = extract_bracket_content(data)
    start_points = []

    for point in [bone_info.find("Translation"), bone_info.find("Rotation"), bone_info.find("Scaling")]:
        if point != -1:
            if re.match('((Translation)|(Rotation)|(Scaling)) \\d', bone_info[point:]):
                start_points.append(point)

    if len(start_points) == 0:
        start_points.append(-1)

    start_point = min(start_points)

    node_chunks = chunkifier(bone_info[start_point:])

    for node_chunk in node_chunks:
        label = node_chunk.strip().split(" ")[0]
        if label == "Translation":
            node.anim_loc = parse_geoset_transformation(node_chunk)
        if label == "Rotation":
            node.anim_rot = parse_geoset_transformation(node_chunk)
        if label == "Scaling":
            node.anim_scale = parse_geoset_transformation(node_chunk)
        if label == "Visibility":
            node.visibility = parse_geoset_transformation(node_chunk)

    return node
