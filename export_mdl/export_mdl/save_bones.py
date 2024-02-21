import itertools
from typing import TextIO

from .write_billboard import write_billboard
from .write_animation_chunk import write_animation_chunk
from ..classes.War3Model import War3Model


def save_bones(fw: TextIO.write, model: War3Model):
    global_seqs = model.global_seqs
    geosets = model.geosets
    geoset_anims = model.geoset_anims
    geoset_anim_map = model.geoset_anim_map
    for bone in model.bones:
        name = bone.name.replace('.', '_')
        # if not name.lower().startswith("bone"):
        #     name = "Bone_" + name

        fw("Bone \"%s\" {\n" % name)
        if 0 <= bone.obj_id:
            fw("\tObjectId %d,\n" % bone.obj_id)
        if bone.parent_id is not None:
            fw("\tParent %d,\n" % bone.parent_id)

        if hasattr(bone, "billboarded"):
            write_billboard(fw, bone.billboarded, bone.billboard_lock)

        children = [g for g in geosets if bone.name in itertools.chain.from_iterable(g.matrices)]
        if len(children) == 1:
            fw("\tGeosetId %d,\n" % geosets.index(children[0]))
        else:
            fw("\tGeosetId -1,\n")

        if bone.name in geoset_anim_map.keys():
            fw("\tGeosetAnimId %d,\n" % geoset_anims.index(geoset_anim_map[bone.name]))
        else:
            fw("\tGeosetAnimId None,\n")

        if bone.anim_loc is not None:
            write_animation_chunk(fw, bone.anim_loc, "Translation", global_seqs, "\t")

        if bone.anim_rot is not None:
            write_animation_chunk(fw, bone.anim_rot, "Rotation", global_seqs, "\t")

        if bone.anim_scale is not None:
            write_animation_chunk(fw, bone.anim_scale, "Scaling", global_seqs, "\t")

        # if bone.anim_loc is not None:
        #     write_animation_chunk(bone.anim_loc.keyframes, bone.anim_loc.type,
        #                           bone.anim_loc.interpolation, bone.anim_loc.global_sequence,
        #                           bone.anim_loc.handles_left, bone.anim_loc.handles_right,
        #               "Translation", fw, global_seqs, "\t")
        #
        # if bone.anim_rot is not None:
        #     write_animation_chunk(bone.anim_rot.keyframes, bone.anim_rot.type,
        #                           bone.anim_rot.interpolation, bone.anim_rot.global_sequence,
        #                           bone.anim_rot.handles_left, bone.anim_rot.handles_right,
        #               "Rotation", fw, global_seqs, "\t")
        #
        # if bone.anim_scale is not None:
        #     write_animation_chunk(bone.anim_scale.keyframes, bone.anim_scale.type,
        #                           bone.anim_scale.interpolation, bone.anim_scale.global_sequence,
        #                           bone.anim_scale.handles_left, bone.anim_scale.handles_right,
        #               "Scaling", fw, global_seqs, "\t")

        # Visibility
        fw("}\n")
