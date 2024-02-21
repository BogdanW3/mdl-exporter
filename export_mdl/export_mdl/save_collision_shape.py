from typing import TextIO, List

from ..classes.War3CollisionShape import War3CollisionShape
from ..utils import float2str, rnd


def save_collision_shape(fw: TextIO.write, collision_shapes: List[War3CollisionShape]):
    for collider in collision_shapes:
        fw("CollisionShape \"%s\" {\n" % collider.name)
        fw("\tObjectId %d,\n" % collider.obj_id)
        if collider.parent_id is not None:
            fw("\tParent %d,\n" % collider.parent_id)
        if collider.type == 'Box':
            fw("\tBox,\n")
        else:
            fw("\tSphere,\n")

        fw("\tVertices %d {\n" % len(collider.verts))
        for vert in collider.verts:
            fw("\t\t{ %s, %s, %s },\n" % tuple(float2str(rnd(x)) for x in list(vert)))
        fw("\t}\n")
        if collider.type == 'Sphere':
            fw("\tBoundsRadius %s,\n" % float2str(rnd(collider.radius)))
        fw("}\n")
