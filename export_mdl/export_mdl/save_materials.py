from .write_animations import write_animations
from ..utils import f2s


def save_materials(fw, model):
    if len(model.materials):
        fw("Materials %d {\n" % len(model.materials))
        for material in model.materials:
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
                    fw("\t\t\tstatic TextureID %d,\n" % model.textures.index(layer.texture))
                else:
                    fw("\t\t\tstatic TextureID 0,\n")

                if layer.texture_anim is not None:
                    fw("\t\t\tTVertexAnimId %d,\n" % model.tvertex_anims.index(layer.texture_anim))
                if layer.alpha_anim is not None:
                    write_animations(layer.alpha_anim.keyframes, layer.alpha_anim.type,
                                     layer.alpha_anim.interpolation, layer.alpha_anim.global_sequence,
                                     layer.alpha_anim.handles_left, layer.alpha_anim.handles_right,
                              "Alpha", fw, model.global_seqs, "\t\t")
                    # write_anim(layer.alpha_anim, "Alpha", fw, global_seqs, "\t\t")
                else:
                    fw("\t\t\tstatic Alpha %s,\n" % f2s(layer.alpha_value))

                fw("\t\t}\n")
            fw("\t}\n")
        fw("}\n")
