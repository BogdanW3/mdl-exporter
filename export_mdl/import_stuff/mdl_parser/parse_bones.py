from .mdl_reader import get_between
from .parse_node import parse_node
from ...classes.War3Bone import War3Bone


def parse_bones(data: str) -> War3Bone:
    bone = War3Bone("")
    bone.geoset_id = 0
    geoset_id = get_between(data, "GeosetId", ",")

    if geoset_id != "Multiple":
        bone.geoset_id = int(geoset_id)

    geoset_animation_id = get_between(data, "GeosetAnimId", ",")
    parse_node(data, bone)

    return bone
