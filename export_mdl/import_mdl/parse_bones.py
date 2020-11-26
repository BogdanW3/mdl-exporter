from ..classes.War3ImportBone import War3ImportBone
from .mdl_reader import get_between
from .parse_node import parse_node


def parse_bones(data, model):
    bone = War3ImportBone()
    bone.geoset_id = 0
    geoset_id = get_between(data, "GeosetId", ",")

    if geoset_id != "Multiple":
        bone.geoset_id = int(geoset_id)

    geosetAnimationId = get_between(data, "GeosetAnimId", ",")
    bone.node = parse_node(data)

    model.nodes.append(bone)
