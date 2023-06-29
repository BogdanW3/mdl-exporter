from typing import List, Set

import bpy

from export_mdl.classes.War3EventObject import War3EventObject
from export_mdl.classes.War3Node import War3Node


def create_event_empties(bone_size: float,
                         nodes: List[War3EventObject],
                         bpy_armature_object: bpy.types.Object):
    node_names: Set[str] = set()
    events: List[bpy.types.Object] = []
    for indexNode, node in enumerate(nodes):
        bpy_object = create_bpy_event(bone_size, node, node_names)
        if node.parent:
            # print(node_name, "location:", bpy_object.location, ", has parent:", node.parent)
            apply_parent_bone(bpy_armature_object, bpy_object, node)
        events.append(bpy_object)
    return events


def create_bpy_event(bone_size: float, node: War3EventObject, node_names: Set[str]):
    node_name = node.name
    if node_name in node_names:
        node_name = node_name + ".001"
        if node_name in node_names:
            node_name = node_name + ".002"
        node.name = node_name
    print(" adding event: \"", node.name + "\"")
    node_names.add(node_name)
    bpy_object = bpy.data.objects.new(node_name, None)
    bpy.context.scene.collection.objects.link(bpy_object)
    bpy_object.location = node.pivot
    bpy_object.empty_display_type = 'CIRCLE'
    bpy_object.empty_display_size = bone_size
    return bpy_object


def apply_parent_bone(bpy_armature_object: bpy.types.Object, bpy_object: bpy.types.Object, node: War3Node):
    bpy_object.parent = bpy_armature_object
    bpy_object.parent_type = 'BONE'
    bpy_object.parent_bone = node.parent
    armature: bpy.types.Armature = bpy_armature_object.data
    parent_bone: bpy.types.Bone = armature.bones.get(node.parent)
    # print(node_name, "has parent:", node.parent, parent_bone)
    if parent_bone:
        bpy_object.location = bpy_object.location - parent_bone.tail
