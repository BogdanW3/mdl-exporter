from typing import TextIO

from mathutils import Vector

from ..classes.War3Model import War3Model
from ..utils import float2str


def save_cameras(fw: TextIO.write, model: War3Model, settings):
    for camera in model.cameras:
        fw("Camera \"%s\" {\n" % camera.name)
        position = settings.global_matrix @ Vector(camera.location)

        fw("\tPosition {%s, %s, %s},\n" % tuple(map(float2str, position)))
        fw("\tFieldOfView %f,\n" % camera.data.angle)
        fw("\tFarClip %f,\n" % (camera.data.clip_end * 10))
        fw("\tNearClip %f,\n" % (camera.data.clip_start * 10))

        matrix = settings.global_matrix @ camera.matrix_world
        target = position + matrix.to_quaternion() @ Vector(
            (0.0, 0.0, -1.0))  # Target is just a point in front of the camera

        fw("\tTarget {\n\t\tPosition {%s, %s, %s},\n\t}\n" % tuple(map(float2str, target)))
        fw("}\n")
