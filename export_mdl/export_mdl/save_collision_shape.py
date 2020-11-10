from ..utils import f2s, rnd


def save_collision_shape(fw, model):
    for collider in model.objects['collisionshape']:
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
            fw("\t\t{%s, %s, %s},\n" % tuple(f2s(rnd(x)) for x in vert))
        fw("\t}\n")
        if collider.type == 'Sphere':
            fw("\tBoundsRadius %s,\n" % f2s(rnd(collider.radius)))
        fw("}\n")
