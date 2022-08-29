from typing import TextIO, Set, List

from io_scene_warcraft_3.classes.WarCraft3Texture import WarCraft3Texture
from .write_animation_chunk import write_animation_chunk
from ..classes.War3Material import War3Material
from ..classes.War3Model import War3Model
from ..classes.War3TextureAnim import War3TextureAnim
from ..utils import float2str


def save_materials(fw: TextIO.write,
                   materials: List[War3Material],
                   textures: List[WarCraft3Texture],
                   tvertex_anims: List[War3TextureAnim],
                   global_seqs: Set[int]):
    if len(materials):
        fw("Materials %d {\n" % len(materials))
        for material in materials:
            fw("\tMaterial {\n")

            if material.use_const_color is True:
                fw("\t\tConstantColor,\n")

            # SortPrimsFarZ,
            # FullResolution,

            if material.priority_plane != 0:
                fw("\t\tPriorityPlane %d,\n" % material.priority_plane)

            for layer in material.layers:
                fw("\t\tLayer {\n")
                fw("\t\t\tFilterMode %s,\n" % layer.filter_mode)
                if layer.unshaded is True:
                    fw("\t\t\tUnshaded,\n")

                if layer.two_sided is True:
                    fw("\t\t\tTwoSided,\n")

                if layer.unfogged is True:
                    fw("\t\t\tUnfogged,\n")

                if layer.no_depth_test:
                    fw("\t\t\tNoDepthTest,\n")

                if layer.no_depth_set:
                    fw("\t\t\tNoDepthSet,\n")

                if layer.texture is not None:
                    fw("\t\t\tstatic TextureID %d,\n" % textures.index(layer.texture))
                else:
                    fw("\t\t\tstatic TextureID 0,\n")

                if layer.texture_anim is not None:
                    fw("\t\t\tTVertexAnimId %d,\n" % tvertex_anims.index(layer.texture_anim))
                if layer.alpha_anim is not None:
                    write_animation_chunk(fw, layer.alpha_anim, "Alpha", global_seqs, "\t\t")
                    # write_animation_chunk(layer.alpha_anim.keyframes, layer.alpha_anim.type,
                    #                       layer.alpha_anim.interpolation, layer.alpha_anim.global_sequence,
                    #                       layer.alpha_anim.handles_left, layer.alpha_anim.handles_right,
                    #           "Alpha", fw, global_seqs, "\t\t")
                else:
                    fw("\t\t\tstatic Alpha %s,\n" % float2str(layer.alpha_value))

                fw("\t\t}\n")
            fw("\t}\n")
        fw("}\n")
