from mathutils import Vector

from ..War3Model import War3Model
from ..War3Object import War3Object
from ...utils import calc_extents


def create_collision_shapes(war3_model: War3Model, bpy_obj, parent, settings):
    collider = War3Object(bpy_obj.name)
    collider.parent = parent
    collider.pivot = settings.global_matrix @ Vector(bpy_obj.location)
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
        collider.verts = [settings.global_matrix @ Vector(bpy_obj.location)]
        collider.radius = settings.global_matrix.median_scale * max(
            abs(x * bpy_obj.empty_display_size) for x in bpy_obj.scale)
        war3_model.objects['collisionshape'].add(collider)
