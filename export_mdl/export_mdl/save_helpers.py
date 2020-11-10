from .write_billboard import write_billboard


def save_helpers(fw, model):
    for helper in model.objects['helper']:
        name = helper.name.replace('.', '_')

        if not name.lower().startswith("bone"):
            name = "Bone_" + name

        fw("Helper \"%s\" {\n" % name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[helper.name])

        if helper.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[helper.parent])

        if hasattr(helper, "billboarded"):
            write_billboard(fw, helper.billboarded, helper.billboard_lock)

        if helper.anim_loc is not None:
            helper.anim_loc.write_mdl("Translation", fw, model.global_seqs, "\t")

        if helper.anim_rot is not None:
            helper.anim_rot.write_mdl("Rotation", fw, model.global_seqs, "\t")

        if helper.anim_scale is not None:
            helper.anim_scale.write_mdl("Scaling", fw, model.global_seqs, "\t")

        fw("}\n")
