from typing import List, Set

import bpy
from mathutils import Vector

from ..classes.War3Model import War3Model
from ..classes.War3Node import War3Node


def create_armature_object(model: War3Model, bone_size: float) -> bpy.types.Object:
    print(" creating armature")
    war3_nodes = list(model.id_to_object.values())
    bpy_armature_object = get_bpy_armature_object(model.name + ' Nodes')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy_armature: bpy.types.Armature = bpy_armature_object.data
    # bpy_armature.display_type = 'STICK'

    create_edit_bones(bone_size, war3_nodes, bpy_armature)
    bpy.ops.object.mode_set(mode='EDIT')

    set_parents(war3_nodes, bpy_armature)
    connect_bones(bpy_armature)
    ensure_bone_length(bpy_armature)

    if bpy.app.version[0] < 4:
        from export_mdl.import_stuff.create_bone_groups import create_bone_groups
        create_bone_groups(war3_nodes, bpy_armature_object)
    else:
        from export_mdl.import_stuff.create_bone_collections import create_bone_groups
        create_bone_groups(war3_nodes, bpy_armature_object)
    bpy.ops.object.mode_set(mode='POSE')

    for p_bone in bpy_armature_object.pose.bones:
        p_bone.rotation_mode = 'QUATERNION'

    return bpy_armature_object


def get_bpy_armature_object(name: str) -> bpy.types.Object:
    bpy_armature: bpy.types.Armature = bpy.data.armatures.new(name)
    bpy_armature_object = bpy.data.objects.new(name, bpy_armature)
    bpy.context.scene.collection.objects.link(bpy_armature_object)
    bpy_armature_object.select_set(True)
    bpy.context.view_layer.objects.active = bpy_armature_object
    # bpy_armature_object.rotation_mode = 'QUATERNION'
    return bpy_armature_object


def create_edit_bones(bone_size: float,
                      nodes: List[War3Node], bpy_armature: bpy.types.Armature):
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones: bpy.types.ArmatureEditBones = bpy_armature.edit_bones
    bone_names: Set[str] = set()
    for node in nodes:
        # print("  adding node \"%s\" (%i)" % (node.name, node.obj_id))
        if node.name in bone_names:
            for i in range(1, 999):
                temp_name = node.name + (".%03.f" % i)
                if temp_name not in bone_names:
                    node.name = temp_name
                    break
        bone = edit_bones.new(node.name)
        bone_names.add(bone.name)
        bone.head = node.pivot
        bone.tail = node.pivot
        bone.tail[2] += bone_size


def set_parents(war3_nodes: List[War3Node], bpy_armature: bpy.types.Armature):
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones: bpy.types.ArmatureEditBones = bpy_armature.edit_bones
    for war3_node in war3_nodes:
        e_bone = edit_bones.get(war3_node.name)
        if war3_node.parent_node is not None:
            war3_par = war3_node.parent_node
            print("connecting \"%s\" (%i) to parent \"%s\" (%i)" % (war3_node.name, war3_node.obj_id,
                                                                    war3_par.name, war3_par.obj_id))
            e_parent = edit_bones.get(war3_par.name)
            e_bone.parent = e_parent
        else:
            print("no parent found for \"%s\" (%i), par: %s" % (war3_node.name, war3_node.obj_id, war3_node.parent))


def connect_bones(bpy_armature: bpy.types.Armature):
    # needs to be done after parents is set to be able to filter bones who is their parents only child
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones: List[bpy.types.EditBone] = bpy_armature.edit_bones.values()
    for e_bone in edit_bones:
        e_parent = e_bone.parent
        if e_parent is not None and len(e_parent.children) == 1:
            e_parent.tail = e_bone.head
            if len(e_bone.children) == 0 and e_parent.length < 0:
                v_dir: Vector = Vector(e_bone.head) - Vector(e_parent.head)
                e_bone.tail = e_bone.head + v_dir


def ensure_bone_length(bpy_armature: bpy.types.Armature):
    # bones with length 0 will be dissolved by blender
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones: bpy.types.ArmatureEditBones = bpy_armature.edit_bones

    tail_offset: Vector = Vector((0, 0, 0.01))  # zero_length_bone_tail_offset
    for bone in edit_bones.values():
        if bone.length < 0.001:
            bone.tail = bone.tail + tail_offset
