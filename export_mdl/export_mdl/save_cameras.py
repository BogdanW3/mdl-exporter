from mathutils import Vector

from ..utils import f2s


def save_cameras(fw, model, settings):
    for camera in model.cameras:
        fw("Camera \"%s\" {\n" % camera.name)
        position = settings.global_matrix @ Vector(camera.location)

        fw("\tPosition {%s, %s, %s},\n" % tuple(map(f2s, position)))
        fw("\tFieldOfView %f,\n" % camera.data.angle)
        fw("\tFarClip %f,\n" % (camera.data.clip_end * 10))
        fw("\tNearClip %f,\n" % (camera.data.clip_start * 10))

        matrix = settings.global_matrix @ camera.matrix_world
        target = position + matrix.to_quaternion() @ Vector(
            (0.0, 0.0, -1.0))  # Target is just a point in front of the camera

        fw("\tTarget {\n\t\tPosition {%s, %s, %s},\n\t}\n" % tuple(map(f2s, target)))
        fw("}\n")
