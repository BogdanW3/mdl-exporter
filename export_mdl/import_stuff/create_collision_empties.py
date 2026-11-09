from typing import List, Set

import bpy
from mathutils import Vector

from export_mdl.classes.War3CollisionShape import War3CollisionShape
from export_mdl.classes.War3Node import War3Node


def create_collision_empties(nodes: List[War3CollisionShape],
                             bpy_armature_object: bpy.types.Object):
    node_names: Set[str] = set()
    collisions: List[bpy.types.Object] = []
    for indexNode, node in enumerate(nodes):
        print("\tCol - adding ", node, " type: ", node.type)
        bpy_object = create_bpy_collision(node, node_names)
        if node.parent:
            apply_parent_bone(bpy_armature_object, bpy_object, node)
        collisions.append(bpy_object)
    return collisions


def apply_parent_bone(bpy_armature_object: bpy.types.Object, bpy_object: bpy.types.Object, node: War3Node):
    bpy_object.parent = bpy_armature_object
    bpy_object.parent_type = 'BONE'
    bpy_object.parent_bone = node.parent
    armature: bpy.types.Armature = bpy_armature_object.data
    parent_bone: bpy.types.Bone = armature.bones.get(node.parent)
    if parent_bone:
        bpy_object.location = bpy_object.location - parent_bone.tail


def create_bpy_collision(node: War3CollisionShape, node_names: Set[str]):
    node_name = node.name
    if not node_name.startswith('Collision'):
        node_name = 'Collision ' + node_name
    if node_name in node_names:
        node_name = node_name + ".001"
        if node_name in node_names:
            node_name = node_name + ".002"
        node.name = node_name
    node_names.add(node_name)
    bpy_object = bpy.data.objects.new(node_name, None)
    bpy.context.scene.collection.objects.link(bpy_object)
    bpy_object.location = node.pivot
    set_collision_display(bpy_object, node)
    return bpy_object


def set_collision_display(bpy_object: bpy.types.Object, node: War3CollisionShape):
    # The shape type is kept on the object, the exporter reads it before guessing from the name or display.
    # So are the file's exact vertices and radius (boxes are relative to the pivot and often lopsided, which an
    # empty's display can't show); the exporter writes them back unchanged.
    bpy_object["mdl_collision_shape"] = node.type
    bpy_object["mdl_collision_vertices"] = [float(c) for vert in node.verts for c in vert]
    if getattr(node, "radius", None) is not None:
        bpy_object["mdl_collision_radius"] = float(node.radius)
    if node.type == 'Cylinder':
        bpy_object.empty_display_size = float(node.radius)
        bpy_object.empty_display_type = 'CIRCLE'
    elif node.type == 'Sphere':
        bpy_object.empty_display_size = float(node.radius)
        bpy_object.empty_display_type = 'SPHERE'
    elif node.type == 'Box':
        bpy_object.empty_display_size = Vector(node.verts[0]).length
        bpy_object.empty_display_type = 'CUBE'
    else:
        bpy_object.empty_display_size = Vector(node.verts[0]).length
        bpy_object.empty_display_type = 'CUBE'
    return bpy_object
