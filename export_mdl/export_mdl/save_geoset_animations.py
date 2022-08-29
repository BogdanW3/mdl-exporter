from typing import TextIO, List, Set

from .write_animation_chunk import write_animation_chunk
from ..classes.War3Geoset import War3Geoset
from ..classes.War3GeosetAnim import War3GeosetAnim
from ..classes.War3Model import War3Model
from ..utils import float2str


def save_geoset_animations(fw: TextIO.write,
                           geoset_anims: List[War3GeosetAnim],
                           geosets: List[War3Geoset],
                           global_seqs: Set[int]):
    if len(geoset_anims):
        for anim in geoset_anims:
            anim.write_geo_anim(fw, geosets.index(anim.geoset), global_seqs)
            # fw("GeosetAnim {\n")
            # alpha = anim.alpha_anim
            # vertex_color = anim.color
            # vertex_color_anim = anim.color_anim
            #
            # if alpha is not None:
            #     write_animation_chunk(fw, alpha, "Alpha", global_seqs, "\t")
            #     # write_animation_chunk(alpha.keyframes, alpha.type,
            #     #                       alpha.interpolation, alpha.global_sequence,
            #     #                       alpha.handles_left, alpha.handles_right,
            #     #           "Alpha", fw, global_seqs, "\t")
            # else:
            #     fw("\tstatic Alpha 1.0,\n")
            #
            # if vertex_color_anim is not None:
            #     write_animation_chunk(fw, vertex_color_anim, "Color", global_seqs, "\t")
            #     # write_animation_chunk(vertex_color_anim.keyframes, vertex_color_anim.type,
            #     #                       vertex_color_anim.interpolation, vertex_color_anim.global_sequence,
            #     #                       vertex_color_anim.handles_left, vertex_color_anim.handles_right,
            #     #           "Color", fw, global_seqs, "\t")
            #
            # elif vertex_color is not None:
            #     fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(float2str, reversed(vertex_color[:3]))))
            #
            # fw("\tGeosetId %d,\n" % geosets.index(anim.geoset))
            #
            # fw("}\n")
