from typing import TextIO, List, Set

from .write_animation_chunk import write_animation_chunk
from ..classes.War3TextureAnim import War3TextureAnim


def save_texture_animations(fw: TextIO.write,
                            tvertex_anims: List[War3TextureAnim],
                            global_seqs: Set[int]):
    if len(tvertex_anims):
        fw("TextureAnims %d {\n" % len(tvertex_anims))
        for uv_anim in tvertex_anims:
            fw("\tTVertexAnim {\n")
            if uv_anim.translation is not None:
                write_animated(fw, uv_anim.translation, global_seqs, "Translation")

            if uv_anim.rotation is not None:
                write_animated(fw, uv_anim.rotation, global_seqs, "Rotation")

            if uv_anim.scale is not None:
                write_animated(fw, uv_anim.scale, global_seqs, "Scaling")

            fw("\t}\n")
        fw("}\n")


def write_animated(fw, anim_curve, global_seqs, name):
    write_animation_chunk(fw, anim_curve, name, global_seqs, "\t\t")
    # write_animation_chunk(anim_curve.keyframes, anim_curve.type,
    #                       anim_curve.interpolation, anim_curve.global_sequence,
    #                       anim_curve.handles_left, anim_curve.handles_right,
    #                       name, fw, global_seqs, "\t\t")
