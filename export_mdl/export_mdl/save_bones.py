import itertools

from export_mdl.export_mdl.write_billboard import write_billboard


def save_bones(fw, model):
    for bone in model.objects['bone']:
        name = bone.name.replace('.', '_')
        if not name.lower().startswith("bone"):
            name = "Bone_" + name

        fw("Bone \"%s\" {\n" % name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[bone.name])
        if bone.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[bone.parent])

        if hasattr(bone, "billboarded"):
            write_billboard(fw, bone.billboarded, bone.billboard_lock)

        children = [g for g in model.geosets if bone.name in itertools.chain.from_iterable(g.matrices)]
        if len(children) == 1:
            fw("\tGeosetId %d,\n" % model.geosets.index(children[0]))
        else:
            fw("\tGeosetId -1,\n")

        if bone.name in model.geoset_anim_map.keys():
            fw("\tGeosetAnimId %d,\n" % model.geoset_anims.index(model.geoset_anim_map[bone.name]))
        else:
            fw("\tGeosetAnimId None,\n")

        if bone.anim_loc is not None:
            bone.anim_loc.write_mdl("Translation", fw, model.global_seqs, "\t")

        if bone.anim_rot is not None:
            bone.anim_rot.write_mdl("Rotation", fw, model.global_seqs, "\t")

        if bone.anim_scale is not None:
            bone.anim_scale.write_mdl("Scaling", fw, model.global_seqs, "\t")

        # Visibility
        fw("}\n")