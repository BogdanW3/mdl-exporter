from typing import TextIO

from .write_mdl import write_mdl
from ..classes.War3Model import War3Model


def save_texture_animations(fw: TextIO.write, model: War3Model):
    if len(model.tvertex_anims):
        fw("TextureAnims %d {\n" % len(model.tvertex_anims))
        for uv_anim in model.tvertex_anims:
            fw("\tTVertexAnim {\n")
            if uv_anim.translation is not None:
                write_mdl(uv_anim.translation.keyframes, uv_anim.translation.type,
                          uv_anim.translation.interpolation, uv_anim.translation.global_sequence,
                          uv_anim.translation.handles_left, uv_anim.translation.handles_right,
                          "Translation", fw, model.global_seqs, "\t\t")

            if uv_anim.rotation is not None:
                write_mdl(uv_anim.rotation.keyframes, uv_anim.rotation.type,
                          uv_anim.rotation.interpolation, uv_anim.rotation.global_sequence,
                          uv_anim.rotation.handles_left, uv_anim.rotation.handles_right,
                          "Rotation", fw, model.global_seqs, "\t\t")

            if uv_anim.scale is not None:
                write_mdl(uv_anim.scaling.keyframes, uv_anim.scaling.type,
                          uv_anim.scaling.interpolation, uv_anim.scaling.global_sequence,
                          uv_anim.scaling.handles_left, uv_anim.scaling.handles_right,
                          "Scaling", fw, model.global_seqs, "\t\t")

            fw("\t}\n")
        fw("}\n")
    material_names = [mat.name for mat in model.materials]
    return material_names
