from typing import List, Dict

import bpy

from ..classes.War3Attachment import War3Attachment
from ..classes.War3Bone import War3Bone
from ..classes.War3CollisionShape import War3CollisionShape
from ..classes.War3EventObject import War3EventObject
from ..classes.War3Helper import War3Helper
from ..classes.War3Light import War3Light
from ..classes.War3Node import War3Node


def create_bone_groups(war3_nodes: List[War3Node], bpy_armature_object: bpy.types.Object):
    bone_to_group_name: Dict[str, str] = get_bone_to_group_name(war3_nodes)
    create_bone_groups1(bone_to_group_name, bpy_armature_object)


def get_bone_to_group_name(war3_nodes: List[War3Node]) -> Dict[str, str]:
    node_to_group: Dict[str, str] = {}
    for war3_node in war3_nodes:
        node_to_group[war3_node.name] = get_group_name(war3_node)
    return node_to_group


def create_bone_groups1(bone_to_group_name: Dict[str, str], bpy_armature_object: bpy.types.Object):
    bpy.ops.object.mode_set(mode='POSE')

    pose_bone_groups: bpy.types.BoneGroups = bpy_armature_object.pose.bone_groups
    for p_bone in bpy_armature_object.pose.bones:
        group_name = bone_to_group_name.get(p_bone.name)
        bone_group: bpy.types.BoneGroup = pose_bone_groups.get(group_name)
        if bone_group is None:
            bone_group = pose_bone_groups.new(name=group_name)
            bone_group.color_set = get_group_color(group_name)

        p_bone.bone_group = bone_group


def get_group_color(nodeType: str) -> str:
    if nodeType == 'bones':
        return 'THEME04'
    elif nodeType == 'attachments':
        return 'THEME09'
    elif nodeType == 'collision_shapes':
        return 'THEME02'
    elif nodeType == 'events':
        return 'THEME03'
    elif nodeType == 'helpers':
        return 'THEME01'
    return 'DEFAULT'


def get_group_name(node: War3Node) -> str:
    if isinstance(node, War3Bone):
        return 'bones'
    elif isinstance(node, War3Helper):
        return 'helpers'
    elif isinstance(node, War3Attachment):
        return 'attachments'
    elif isinstance(node, War3CollisionShape):
        return 'collision_shapes'
    elif isinstance(node, War3Light):
        return 'lights'
    elif isinstance(node, War3EventObject):
        return 'events'
    return 'defaults'
