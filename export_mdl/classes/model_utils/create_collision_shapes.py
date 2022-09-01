from typing import List, Optional

import bpy
from mathutils import Vector, Matrix

from ..War3CollisionShape import War3CollisionShape
from ..War3ExportSettings import War3ExportSettings
from ..bpy_helpers.BpyEmptyNode import BpyEmptyNode
from ...utils import calc_extents


def create_collision_shapes(bpy_obj: bpy.types.Object,
                            parent_name: Optional[str],
                            settings: War3ExportSettings):
    pivot = settings.global_matrix @ Vector(bpy_obj.location)
    collider = War3CollisionShape(bpy_obj.name, None, None, None, parent_name, pivot)
    if 'Box' in bpy_obj.name:
        collider.type = 'Box'
        corners: List[List[float]] = []
        for corner in ((0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, 0.5, -0.5),
                       (0.5, 0.5, 0.5),  (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5)):
            mat = settings.global_matrix @ bpy_obj.matrix_world
            corners.append(mat.to_quaternion() @ Vector(
                abs(x * bpy_obj.empty_display_size * settings.global_matrix.median_scale) * y for x, y in
                zip(bpy_obj.scale, corner)))

        v_min, v_max = calc_extents(corners)

        collider.verts.extend([v_min, v_max])  # TODO: World space or relative to pivot??
    elif 'Sphere' in bpy_obj.name:
        collider.type = 'Sphere'
        collider.verts.append([pivot])
        collider.radius = settings.global_matrix.median_scale * max(
            abs(x * bpy_obj.empty_display_size) for x in bpy_obj.scale)
    elif 'Cylinder' in bpy_obj.name:
        collider.type = 'Cylinder'
        collider.verts.append([pivot])
        collider.radius = settings.global_matrix.median_scale * max(
            abs(x * bpy_obj.empty_display_size) for x in bpy_obj.scale)
    return collider


def create_collision_shapes(bpy_empty_node: BpyEmptyNode,
                            global_matrix: Matrix):
    pivot = global_matrix @ Vector(bpy_empty_node.location)
    collider = War3CollisionShape(bpy_empty_node.name, None, None, None, bpy_empty_node.parent_name, pivot,
                                  bpy_empty_node.bpy_obj.matrix_basis)
    if 'Box' in bpy_empty_node.name \
            or bpy_empty_node.display_type == 'CUBE' \
            and 'Sphere' not in bpy_empty_node.name \
            and 'Cylinder' not in bpy_empty_node.name:
        collider.type = 'Box'
        corners: List[List[float]] = []
        # for corner in ((0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, 0.5, -0.5),
        #                (0.5, 0.5, 0.5),  (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5)):
        for corner in ((1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, 1, -1),
                       (1, 1, 1),  (-1, -1, 1), (1, -1, 1), (-1, 1, 1)):
            mat = global_matrix @ bpy_empty_node.bpy_obj.matrix_world
            corners.append(mat.to_quaternion() @ Vector(
                abs(x * bpy_empty_node.bpy_obj.empty_display_size * global_matrix.median_scale) * y for x, y in
                zip(bpy_empty_node.bpy_obj.scale, corner)))

        v_min, v_max = calc_extents(corners)

        collider.verts.extend([v_min, v_max])  # TODO: World space or relative to pivot??
    elif 'Sphere' in bpy_empty_node.name or bpy_empty_node.display_type == 'SPHERE':
        collider.type = 'Sphere'
        collider.verts.append([pivot])
        collider.radius = global_matrix.median_scale * max(
            abs(x * bpy_empty_node.bpy_obj.empty_display_size) for x in bpy_empty_node.bpy_obj.scale)
    # elif 'Cylinder' in bpy_empty_node.name:
    else:
        collider.type = 'Cylinder'
        collider.verts.append([pivot])
        collider.radius = global_matrix.median_scale * max(
            abs(x * bpy_empty_node.bpy_obj.empty_display_size) for x in bpy_empty_node.bpy_obj.scale)
    return collider
