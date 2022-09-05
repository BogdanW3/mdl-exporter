from typing import Optional, TextIO, List, Set

from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.export_mdl.write_animation_chunk import write_animation_chunk
from export_mdl.utils import float2str


class War3GeosetAnim:
    def __init__(self, color,
                 color_anim: Optional[War3AnimationCurve],
                 alpha_anim: Optional[War3AnimationCurve]):
        self.color = color
        self.color_anim: Optional[War3AnimationCurve] = color_anim
        self.alpha_anim: Optional[War3AnimationCurve] = alpha_anim
        self.geoset = None
        self.geoset_name = "0"
        self.geoset_id: int = 0

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            if self.color != other.color and not any((self.color_anim, other.color_anim)):  # Color doesn't matter if there is an animation
                return False

            if self.geoset is not other.geoset:
                return False

            if self.alpha_anim != other.alpha_anim:
                return False

            if self.color_anim != other.color_anim:
                return False

            return True

        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        color_hash = 0 if self.color is None else hash(self.color)
        return hash((hash(self.color_anim), hash(self.alpha_anim), color_hash))

    def write_geo_anim(self, fw: TextIO.write, geoset_id: int, global_seqs: Set[int]):
        fw("GeosetAnim {\n")

        if self.alpha_anim is not None:
            write_animation_chunk(fw, self.alpha_anim, "Alpha", global_seqs, "\t")
            # write_animation_chunk(alpha.keyframes, alpha.type,
            #                       alpha.interpolation, alpha.global_sequence,
            #                       alpha.handles_left, alpha.handles_right,
            #           "Alpha", fw, global_seqs, "\t")
        else:
            fw("\tstatic Alpha 1.0,\n")

        if self.color_anim is not None:
            write_animation_chunk(fw, self.color_anim, "Color", global_seqs, "\t")
            # write_animation_chunk(vertex_color_anim.keyframes, vertex_color_anim.type,
            #                       vertex_color_anim.interpolation, vertex_color_anim.global_sequence,
            #                       vertex_color_anim.handles_left, vertex_color_anim.handles_right,
            #           "Color", fw, global_seqs, "\t")

        elif self.color is not None:
            fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(float2str, reversed(self.color[:3]))))

        fw("\tGeosetId %d,\n" % geoset_id)

        fw("}\n")
