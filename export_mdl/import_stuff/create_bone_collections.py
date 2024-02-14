from typing import List, Dict

import bpy

from export_mdl.classes.War3Attachment import War3Attachment
from export_mdl.classes.War3Bone import War3Bone
from export_mdl.classes.War3CollisionShape import War3CollisionShape
from export_mdl.classes.War3EventObject import War3EventObject
from export_mdl.classes.War3Helper import War3Helper
from export_mdl.classes.War3Light import War3Light
from export_mdl.classes.War3Node import War3Node


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

    bone_collections: bpy.types.BoneCollections = bpy_armature_object.data.collections
    for p_bone in bpy_armature_object.pose.bones:
        group_name = bone_to_group_name.get(p_bone.name)
        collection: bpy.types.BoneCollection = bone_collections.get(group_name)
        if collection is None:
            collection = bone_collections.new(name=group_name)

        p_bone.bone.collections.clear()
        collection.assign(p_bone.bone)
        p_bone.color.palette = get_group_color(group_name)
        p_bone.bone.color.palette = get_group_color(group_name)


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
