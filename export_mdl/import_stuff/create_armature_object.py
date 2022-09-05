from typing import List, Dict, Set

import bpy
from mathutils import Matrix, Vector

from export_mdl.classes.War3Attachment import War3Attachment
from export_mdl.classes.War3Bone import War3Bone
from export_mdl.classes.War3CollisionShape import War3CollisionShape
from export_mdl.classes.War3EventObject import War3EventObject
from export_mdl.classes.War3Helper import War3Helper
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Node import War3Node


def create_armature_object(model: War3Model, bone_size: float) -> bpy.types.Object:
    print("creating armature")
    war3_nodes = model.objects_all
    war3_node_inds = model.object_indices
    bpy_armature_object = get_bpy_armature_object(model.name + ' Nodes')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy_armature: bpy.types.Armature = bpy_armature_object.data
    # bpy_armature.display_type = 'STICK'

    create_edit_bones(bone_size, bpy_armature.edit_bones, war3_nodes)

    print(bpy_armature.edit_bones[0])

    edit_bones = bpy_armature.edit_bones
    for indexNode, war3_node in enumerate(war3_nodes):
        e_bone = edit_bones[indexNode]
        if war3_node.parent is not None:
            e_parent = edit_bones[war3_node_inds[war3_node.parent]]
            e_bone.parent = e_parent

    set_parents_and_connect_bones(edit_bones, war3_nodes, war3_node_inds)

    bpy.ops.object.mode_set(mode='EDIT')
    bone_types: Dict[str, str] = {}
    for node in war3_nodes:
        bone_types[node.name] = get_node_type(node)

    for a_bone in bpy_armature.bones:
        a_bone.war_3.nodeType = bone_types[a_bone.name].upper()

    bpy.ops.object.mode_set(mode='POSE')

    pose_bone_groups: bpy.types.BoneGroups = bpy_armature_object.pose.bone_groups
    node_types: List[str] = sorted(set(bone_types.values()))
    create_bone_groups(node_types, pose_bone_groups)
    bone_groups = get_bone_group_dict(node_types, pose_bone_groups)

    for p_bone in bpy_armature_object.pose.bones:
        p_bone.rotation_mode = 'QUATERNION'
        p_bone.bone_group = bone_groups[bone_types[p_bone.name]]

    return bpy_armature_object


def set_parents_and_connect_bones(edit_bones, war3_nodes, war3_node_inds):
    for indexNode, war3_node in enumerate(war3_nodes):
        e_bone = edit_bones[indexNode]
        if war3_node.parent is not None:
            e_parent = edit_bones[war3_node_inds[war3_node.parent]]
            e_bone.parent = e_parent

    # connecting needs to be done after parents is set to be able to filter bones who is their parents only child
    for indexNode, war3_node in enumerate(war3_nodes):
        e_bone = edit_bones[indexNode]
        e_parent = e_bone.parent
        if e_parent is not None:
            if len(e_parent.children) == 1:
                e_parent.tail = e_bone.head
                if len(e_bone.children) == 0:
                    v_dir: Vector = Vector(e_bone.head) - Vector(e_parent.head)
                    if 0 < v_dir.length:
                        e_bone.tail = e_bone.head + v_dir


def get_bpy_armature_object(name: str) -> bpy.types.Object:
    bpy_armature: bpy.types.Armature = bpy.data.armatures.new(name)
    bpy_armature_object = bpy.data.objects.new(name, bpy_armature)
    bpy.context.scene.collection.objects.link(bpy_armature_object)
    bpy_armature_object.select_set(True)
    bpy.context.view_layer.objects.active = bpy_armature_object
    # bpy_armature_object.rotation_mode = 'QUATERNION'
    return bpy_armature_object


def create_bone_groups(node_types: List[str], pose_bone_groups: bpy.types.BoneGroups):
    for node_type in node_types:
        bone_group: bpy.types.BoneGroup = pose_bone_groups.get(node_type + 's')
        if bone_group is None:
            bone_group = pose_bone_groups.new(name=node_type + 's')
            bone_group.color_set = get_bone_group_color(node_type)


def get_bone_group_dict(node_types: List[str], pose_bone_groups: bpy.types.BoneGroups):
    bone_groups: Dict[str, bpy.types.BoneGroup] = {}
    for node_type in node_types:
        bone_groups[node_type] = pose_bone_groups.get(node_type + 's')
    return bone_groups


def create_edit_bones(bone_size: float,
                      edit_bones: bpy.types.ArmatureEditBones,
                      nodes: List[War3Node]):
    bone_names: Set[str] = set()
    for indexNode, node in enumerate(nodes):
        print("adding ", node)
        bone_name = node.name
        if bone_name in bone_names:
            bone_name = bone_name + ".001"
            if bone_name in bone_names:
                bone_name = bone_name + ".002"
            node.name = bone_name
        bone_names.add(bone_name)
        bone = edit_bones.new(bone_name)
        bone.head = node.pivot
        bone.tail = node.pivot
        bone.tail[2] += bone_size


def get_bone_group_color(nodeType) -> str:
    if nodeType == 'bone':
        return 'THEME04'
    elif nodeType == 'attachment':
        return 'THEME09'
    elif nodeType == 'collision_shape':
        return 'THEME02'
    elif nodeType == 'event':
        return 'THEME03'
    elif nodeType == 'helper':
        return 'THEME01'
    return 'DEFAULT'


def get_node_type(node: War3Node) -> str:
    if isinstance(node, War3Bone):
        return 'bone'
    elif isinstance(node, War3Attachment):
        return 'attachment'
    elif isinstance(node, War3CollisionShape):
        return 'collision_shape'
    elif isinstance(node, War3EventObject):
        return 'event'
    elif isinstance(node, War3Helper):
        return 'helper'
    return 'default'
