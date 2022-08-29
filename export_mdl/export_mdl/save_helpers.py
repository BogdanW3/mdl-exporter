from typing import TextIO

from .write_billboard import write_billboard
from .write_animation_chunk import write_animation_chunk
from ..classes.War3Model import War3Model


def save_helpers(fw: TextIO.write, model: War3Model):
    for helper in model.helpers:
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
            write_animation_chunk(fw, helper.anim_loc, "Translation", model.global_seqs, "\t")

        if helper.anim_rot is not None:
            write_animation_chunk(fw, helper.anim_rot, "Rotation", model.global_seqs, "\t")

        if helper.anim_scale is not None:
            write_animation_chunk(fw, helper.anim_scale, "Scaling", model.global_seqs, "\t")

        # if helper.anim_loc is not None:
        #     write_animation_chunk(helper.anim_loc.keyframes, helper.anim_loc.type,
        #                           helper.anim_loc.interpolation, helper.anim_loc.global_sequence,
        #                           helper.anim_loc.handles_left, helper.anim_loc.handles_right,
        #               "Translation", fw, model.global_seqs, "\t")
        #
        # if helper.anim_rot is not None:
        #     write_animation_chunk(helper.anim_rot.keyframes, helper.anim_rot.type,
        #                           helper.anim_rot.interpolation, helper.anim_rot.global_sequence,
        #                           helper.anim_rot.handles_left, helper.anim_rot.handles_right,
        #               "Rotation", fw, model.global_seqs, "\t")
        #
        # if helper.anim_scale is not None:
        #     write_animation_chunk(helper.anim_scale.keyframes, helper.anim_scale.type,
        #                           helper.anim_scale.interpolation, helper.anim_scale.global_sequence,
        #                           helper.anim_scale.handles_left, helper.anim_scale.handles_right,
        #               "Scaling", fw, model.global_seqs, "\t")

        fw("}\n")
