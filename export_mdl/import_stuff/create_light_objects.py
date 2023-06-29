from typing import List

import bpy

from export_mdl.classes.War3Light import War3Light
from export_mdl.classes.War3Node import War3Node
from export_mdl.properties import War3LightSettings


def create_light_objects(nodes: List[War3Light], bpy_armature_object: bpy.types.Object):
    print("  Creating lights!")
    lights: List[bpy.types.Object] = []

    for indexNode, node in enumerate(nodes):
        print("   adding light \"" + node.name + "\", type: ", node.light_type)
        bpy_object = create_bpy_light(node)
        if node.parent:
            print("    has parent: ", node.parent)
            apply_parent_bone(bpy_armature_object, bpy_object, node)
        lights.append(bpy_object)

    return lights


def create_bpy_light(node):
    bpy_light: bpy.types.Light = bpy.data.lights.new(node.name, type="POINT")
    bpy_light.energy = node.intensity
    bpy_light.color = node.color
    if hasattr(bpy_light, 'mdl_light'):
        light_settings: War3LightSettings = bpy_light.__getattribute__('mdl_light')
        light_settings.light_type = node.light_type
        # light_settings.light_type = ('Omnidirectional', 'Directional', 'Ambient')[node.light_type]
        light_settings.atten_start = node.atten_start
        light_settings.atten_end = node.atten_end
        light_settings.color = node.color
        light_settings.intensity = node.intensity
        light_settings.amb_color = node.amb_color
        light_settings.amb_intensity = node.amb_intensity
    bpy_object = bpy.data.objects.new(node.name, bpy_light)
    bpy.context.scene.collection.objects.link(bpy_object)
    bpy_object.location = node.pivot
    return bpy_object


def apply_parent_bone(bpy_armature_object: bpy.types.Object, bpy_object: bpy.types.Object, node: War3Node):
    bpy_object.parent = bpy_armature_object
    bpy_object.parent_type = 'BONE'
    bpy_object.parent_bone = node.parent
    armature: bpy.types.Armature = bpy_armature_object.data
    parent_bone: bpy.types.Bone = armature.bones.get(node.parent)
    if parent_bone:
        matrix_inverted = parent_bone.matrix.inverted().to_4x4()
        bpy_object.matrix_parent_inverse = matrix_inverted
        bpy_object.location = bpy_object.location - parent_bone.tail
