import itertools

from .write_billboard import write_billboard
from .write_mdl import write_mdl


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
            write_mdl(bone.anim_loc.keyframes, bone.anim_loc.type, bone.anim_loc.interpolation,
                      bone.anim_loc.global_sequence, bone.anim_loc.handles_left, bone.anim_loc.handles_right,
                      "Translation", fw, model.global_seqs, "\t")

        if bone.anim_rot is not None:
            write_mdl(bone.anim_rot.keyframes, bone.anim_rot.type, bone.anim_rot.interpolation,
                      bone.anim_rot.global_sequence, bone.anim_rot.handles_left, bone.anim_rot.handles_right,
                      "Rotation", fw, model.global_seqs, "\t")

        if bone.anim_scale is not None:
            write_mdl(bone.anim_scale.keyframes, bone.anim_scale.type, bone.anim_scale.interpolation,
                      bone.anim_scale.global_sequence, bone.anim_scale.handles_left, bone.anim_scale.handles_right,
                      "Scaling", fw, model.global_seqs, "\t")

        # Visibility
        fw("}\n")
