import typing

import bpy
from mathutils import Vector

from ..War3CollisionShape import War3CollisionShape
from ..War3ExportSettings import War3ExportSettings
from ..War3Model import War3Model
from ..War3Node import War3Node
from ...utils import calc_extents


def create_collision_shapes(war3_model: War3Model, bpy_obj: bpy.types.Object,
                            parent: typing.Optional[bpy.types.Object],
                            settings: War3ExportSettings):
    # collider = War3Object(bpy_obj.name)
    if parent is not None:
        c_parent = parent.name
    else:
        c_parent = None
    pivot = settings.global_matrix @ Vector(bpy_obj.location)
    collider = War3CollisionShape(bpy_obj.name, None, None, None, c_parent, pivot)
    # collider.parent = parent
    # collider.pivot = pivot
    if 'Box' in bpy_obj.name:
        collider.type = 'Box'
        corners = []
        for corner in ((0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
                       (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.5, 0.5)):
            mat = settings.global_matrix @ bpy_obj.matrix_world
            corners.append(mat.to_quaternion() @ Vector(
                abs(x * bpy_obj.empty_display_size * settings.global_matrix.median_scale) * y for x, y in
                zip(bpy_obj.scale, corner)))

        vmin, vmax = calc_extents(corners)

        collider.verts = [vmin, vmax]  # TODO: World space or relative to pivot??
        war3_model.objects['collisionshape'].add(collider)
    elif 'Sphere' in bpy_obj.name:
        collider.type = 'Sphere'
        collider.verts = [pivot]
        collider.radius = settings.global_matrix.median_scale * max(
            abs(x * bpy_obj.empty_display_size) for x in bpy_obj.scale)
        war3_model.objects['collisionshape'].add(collider)
