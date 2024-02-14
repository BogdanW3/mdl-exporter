import re

from .parse_geoset_transformation import parse_geoset_transformation
from .mdl_reader import get_between, extract_bracket_content, chunkifier
from ...classes.War3Node import War3Node


def parse_node(data: str, node: War3Node):
    # print("parse_node")
    node.name = data.split("\"")[1]
    node.obj_id = 0
    if data.find("ObjectId") > -1:
        node_id = get_between(data, "ObjectId", ",")
        node.obj_id = int(node_id)

    node.parent = None
    if data.find("Parent") > -1:
        node.parent = get_between(data, "Parent", ",")

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
            node.anim_loc.type = "Translation"
        if label == "Rotation":
            node.anim_rot = parse_geoset_transformation(node_chunk)
            node.anim_rot.type = "Rotation"
        if label == "Scaling":
            node.anim_scale = parse_geoset_transformation(node_chunk)
            node.anim_scale.type = "Scaling"
        if label == "Visibility":
            node.visibility = parse_geoset_transformation(node_chunk)
            node.visibility.type = "Visibility"

    return node
