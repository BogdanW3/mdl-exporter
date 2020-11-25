from .write_mdl import write_mdl
from ..utils import f2s


def save_geoset_animations(fw, model):
    if len(model.geoset_anims):
        for anim in model.geoset_anims:
            fw("GeosetAnim {\n")
            alpha = anim.alpha_anim
            vertex_color = anim.color
            vertex_color_anim = anim.color_anim

            if alpha is not None:
                write_mdl(alpha.keyframes, alpha.type,
                          alpha.interpolation, alpha.global_sequence,
                          alpha.handles_left, alpha.handles_right,
                          "Alpha", fw, model.global_seqs, "\t")
            else:
                fw("\tstatic Alpha 1.0,\n")

            if vertex_color_anim is not None:
                write_mdl(vertex_color_anim.keyframes, vertex_color_anim.type,
                          vertex_color_anim.interpolation, vertex_color_anim.global_sequence,
                          vertex_color_anim.handles_left, vertex_color_anim.handles_right,
                          "Color", fw, model.global_seqs, "\t")

            elif vertex_color is not None:
                fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(f2s, reversed(vertex_color[:3]))))

            fw("\tGeosetId %d,\n" % model.geosets.index(anim.geoset))

            fw("}\n")
