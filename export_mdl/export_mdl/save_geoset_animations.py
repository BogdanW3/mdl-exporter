from .write_mdl import write_mdl
from ..utils import f2s


def save_geoset_animations(fw, model):
    if len(model.geoset_anims):
        for anim in model.geoset_anims:
            fw("GeosetAnim {\n")
            alpha = anim.alpha_anim
            vertexcolor = anim.color
            vertexcolor_anim = anim.color_anim
            if alpha is not None:
                write_mdl(alpha.keyframes, alpha.type, alpha.interpolation, alpha.global_sequence, alpha.handles_left,
                          alpha.handles_right, "Alpha", fw, model.global_seqs, "\t")
            else:
                fw("\tstatic Alpha 1.0,\n")

            if vertexcolor_anim is not None:
                write_mdl(vertexcolor_anim.keyframes, vertexcolor_anim.type, vertexcolor_anim.interpolation,
                          vertexcolor_anim.global_sequence, vertexcolor_anim.handles_left,
                          vertexcolor_anim.handles_right, "Color", fw, model.global_seqs, "\t")
            elif vertexcolor is not None:
                fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(f2s, reversed(vertexcolor[:3]))))

            fw("\tGeosetId %d,\n" % model.geosets.index(anim.geoset))

            fw("}\n")
