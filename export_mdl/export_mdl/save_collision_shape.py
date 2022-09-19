from typing import TextIO

from ..classes.War3Model import War3Model
from ..utils import float2str, rnd


def save_collision_shape(fw: TextIO.write, model: War3Model):
    for collider in model.collision_shapes:
        fw("CollisionShape \"%s\" {\n" % collider.name)
        fw("\tObjectId %d,\n" % model.object_indices[collider.name])
        if collider.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[collider.parent])
        if collider.type == 'Box':
            fw("\tBox,\n")
        else:
            fw("\tSphere,\n")

        fw("\tVertices %d {\n" % len(collider.verts))
        for vert in collider.verts:
            fw("\t\t{%s, %s, %s},\n" % tuple(float2str(rnd(x)) for x in list(vert)))
        fw("\t}\n")
        if collider.type == 'Sphere':
            fw("\tBoundsRadius %s,\n" % float2str(rnd(collider.radius)))
        fw("}\n")
