from typing import Optional, List, TextIO, Set, Dict

import bpy
from mathutils import Vector, Matrix

from .War3Texture import War3Texture
from ..export_mdl.write_animation_chunk import write_animation_chunk
from ..utils import float2str, rnd
from .War3Node import War3Node
from .War3AnimationCurve import War3AnimationCurve
from ..properties import War3ParticleSystemProperties


class War3Emitter(War3Node):
    def __init__(self, name: str,
                 pivot: List[float] = [0, 0, 0],
                 parent: Optional[str] = None,
                 anim_loc: Optional[War3AnimationCurve] = None,
                 anim_rot: Optional[War3AnimationCurve] = None,
                 anim_scale: Optional[War3AnimationCurve] = None,
                 bindpose: Optional[Matrix] = None):
        super().__init__(name, pivot, parent, anim_loc, anim_rot, anim_scale, bindpose)
        self.emission_rate_anim: Optional[War3AnimationCurve] = None
        self.life_span_anim: Optional[War3AnimationCurve] = None
        self.gravity_anim: Optional[War3AnimationCurve] = None
        self.alpha_anim: Optional[War3AnimationCurve] = None
        self.visibility: Optional[War3AnimationCurve] = None
        self.emitter: War3ParticleSystemProperties = None

    @classmethod
    def create_from(cls, node: 'War3Node'):
        return War3Emitter(node.name, node.pivot, node.parent,
                           node.anim_loc, node.anim_rot, node.anim_scale,
                           node.bindpose)
    # def set_from(self, obj: bpy.types.Object, sequences: List[War3AnimationAction], global_seqs: Set[int]):
    #     settings: bpy.types.ParticleSettings = obj.particle_systems[0].settings
    #
    #     self.emitter: War3ParticleSystemProperties = settings.mdl_particle_sys
    #     self.scale_anim: Optional[War3AnimationCurve] = get_anim(obj.animation_data, 'scale', 2, sequences)
    #     self.register_global_sequence(global_seqs, self.scale_anim)
    #     # register_global_sequence(model.global_seqs, self.scale_anim)
    #
    #     # Animated properties
    #     bby_anim_data = settings.animation_data
    #     if bby_anim_data is None:
    #         self.emission_rate_anim: Optional[War3AnimationCurve] = None
    #         self.speed_anim: Optional[War3AnimationCurve] = None
    #         self.life_span_anim: Optional[War3AnimationCurve] = None
    #         self.gravity_anim: Optional[War3AnimationCurve] = None
    #         self.variation_anim: Optional[War3AnimationCurve] = None
    #         self.latitude_anim: Optional[War3AnimationCurve] = None
    #         self.longitude_anim: Optional[War3AnimationCurve] = None
    #         self.alpha_anim: Optional[War3AnimationCurve] = None
    #         self.ribbon_color_anim: Optional[War3AnimationCurve] = None
    #     else:
    #         self.emission_rate_anim = get_anim(bby_anim_data, 'mdl_particle_sys.emission_rate', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.emission_rate_anim)
    #         # register_global_sequence(model.global_seqs, self.emission_rate_anim)
    #
    #         self.speed_anim = get_anim(bby_anim_data, 'mdl_particle_sys.speed', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.speed_anim)
    #         # register_global_sequence(model.global_seqs, self.speed_anim)
    #
    #         self.life_span_anim = get_anim(bby_anim_data, 'mdl_particle_sys.life_span', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.life_span_anim)
    #         # register_global_sequence(model.global_seqs, self.life_span_anim)
    #
    #         self.gravity_anim = get_anim(bby_anim_data, 'mdl_particle_sys.gravity', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.gravity_anim)
    #         # register_global_sequence(model.global_seqs, self.gravity_anim)
    #
    #         self.variation_anim = get_anim(bby_anim_data, 'mdl_particle_sys.variation', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.variation_anim)
    #         # register_global_sequence(model.global_seqs, self.variation_anim)
    #
    #         self.latitude_anim = get_anim(bby_anim_data, 'mdl_particle_sys.latitude', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.latitude_anim)
    #         # register_global_sequence(model.global_seqs, self.latitude_anim)
    #
    #         self.longitude_anim = get_anim(bby_anim_data, 'mdl_particle_sys.longitude', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.longitude_anim)
    #         # register_global_sequence(model.global_seqs, self.longitude_anim)
    #
    #         self.alpha_anim = get_anim(bby_anim_data, 'mdl_particle_sys.alpha', 1, sequences)
    #         self.register_global_sequence(global_seqs, self.alpha_anim)
    #         # register_global_sequence(model.global_seqs, self.alpha_anim)
    #
    #         self.ribbon_color_anim = get_anim(bby_anim_data, 'mdl_particle_sys.ribbon_color', 3, sequences)
    #         self.register_global_sequence(global_seqs, self.ribbon_color_anim)
    #         # register_global_sequence(model.global_seqs, self.ribbon_color_anim)

    def write_particle(self, fw: TextIO.write,
                       object_indices: Dict[str, int],
                       global_seqs: Set[int],
                       textures: List[War3Texture]):
        fw("ParticleEmitter2 \"%s\" {\n" % self.name)
        if len(object_indices) > 1:
            fw("\tObjectId %d,\n" % object_indices[self.name])
        if self.parent is not None:
            fw("\tParent %d,\n" % object_indices[self.parent])

        if self.emitter.sort_far_z:
            fw("\tSortPrimsFarZ,\n")

        if self.emitter.unshaded:
            fw("\tUnshaded,\n")

        if self.emitter.line_emitter:
            fw("\tLineEmitter,\n")

        if self.emitter.unfogged:
            fw("\tUnfogged,\n")

        if self.emitter.model_space:
            fw("\tModelSpace,\n")

        if self.emitter.xy_quad:
            fw("\tXYQuad,\n")

        if self.speed_anim is not None:
            write_animation_chunk(fw, self.speed_anim, "Speed", global_seqs, "\t")
            # write_animation_chunk(self.speed_anim.keyframes, self.speed_anim.type,
            #                       self.speed_anim.interpolation, self.speed_anim.global_sequence,
            #                       self.speed_anim.handles_left, self.speed_anim.handles_right,
            #                       "Speed", fw, global_seqs, "\t")
        else:
            fw("\tstatic Speed %s,\n" % float2str(rnd(self.emitter.speed)))

        if self.variation_anim is not None:
            write_animation_chunk(fw, self.variation_anim, "Variation", global_seqs, "\t")
            # write_animation_chunk(self.variation_anim.keyframes, self.variation_anim.type,
            #                       self.variation_anim.interpolation, self.variation_anim.global_sequence,
            #                       self.variation_anim.handles_left, self.variation_anim.handles_right,
            #                       "Variation", fw, global_seqs, "\t")
        else:
            fw("\tstatic Variation %s,\n" % float2str(rnd(self.emitter.variation)))

        if self.latitude_anim is not None:
            write_animation_chunk(fw, self.latitude_anim, "Latitude", global_seqs, "\t")
            # write_animation_chunk(self.latitude_anim.keyframes, self.latitude_anim.type,
            #                       self.latitude_anim.interpolation, self.latitude_anim.global_sequence,
            #                       self.latitude_anim.handles_left, self.latitude_anim.handles_right,
            #                       "Latitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Latitude %s,\n" % float2str(rnd(self.emitter.latitude)))

        if self.gravity_anim is not None:
            write_animation_chunk(fw, self.gravity_anim, "Gravity", global_seqs, "\t")
            # write_animation_chunk(self.gravity_anim.keyframes, self.gravity_anim.type,
            #                       self.gravity_anim.interpolation, self.gravity_anim.global_sequence,
            #                       self.gravity_anim.handles_left, self.gravity_anim.handles_right,
            #                       "Gravity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Gravity %s,\n" % float2str(rnd(self.emitter.gravity)))

        if self.visibility is not None:
            write_animation_chunk(fw, self.visibility, "Visibility", global_seqs, "\t")
            # write_animation_chunk(self.visibility.keyframes, self.visibility.type,
            #                       self.visibility.interpolation, self.visibility.global_sequence,
            #                       self.visibility.handles_left, self.visibility.handles_right,
            #                       "Visibility", fw, global_seqs, "\t")

        fw("\tLifeSpan %s,\n" % float2str(rnd(self.emitter.life_span)))

        if self.emission_rate_anim is not None:
            write_animation_chunk(fw, self.emission_rate_anim, "EmissionRate", global_seqs, "\t")
            # write_animation_chunk(self.emission_rate_anim.keyframes, self.emission_rate_anim.type,
            #                       self.emission_rate_anim.interpolation, self.emission_rate_anim.global_sequence,
            #                       self.emission_rate_anim.handles_left, self.emission_rate_anim.handles_right,
            #                       "EmissionRate", fw, global_seqs, "\t")
        else:
            fw("\tstatic EmissionRate %s,\n" % float2str(rnd(self.emitter.emission_rate)))

        # FIXME FIXME FIXME FIXME FIXME: Separate X and Y channels! New animation class won't handle this.
        if self.scale_anim is not None and ('scale', 1) in self.scale_anim.keys():
            write_animation_chunk(fw, self.scale_anim, "Width", global_seqs, "\t")
            # write_animation_chunk(self.scale_anim.keyframes, self.scale_anim.type,
            #                       self.scale_anim.interpolation, self.scale_anim.global_sequence,
            #                       self.scale_anim.handles_left, self.scale_anim.handles_right,
            #                       "Width", fw, global_seqs, "\t")
        else:
            fw("\tstatic Width %s,\n" % float2str(rnd(self.dimensions[1])))

        if self.scale_anim is not None and ('scale', 0) in self.scale_anim.keys():
            write_animation_chunk(fw, self.scale_anim, "Length", global_seqs, "\t")
            # write_animation_chunk(self.scale_anim.keyframes, self.scale_anim.type,
            #                       self.scale_anim.interpolation, self.scale_anim.global_sequence,
            #                       self.scale_anim.handles_left, self.scale_anim.handles_right,
            #                       "Length", fw, global_seqs, "\t")
        else:
            fw("\tstatic Length %s,\n" % float2str(rnd(self.dimensions[0])))

        fw("\t%s,\n" % self.emitter.filter_mode)
        fw("\tRows %d,\n" % self.emitter.rows)
        fw("\tColumns %d,\n" % self.emitter.cols)

        if self.emitter.head and self.emitter.tail:
            fw("\tBoth,\n")
        elif self.emitter.tail:
            fw("\tTail,\n")
        else:
            fw("\tHead,\n")

        fw("\tTailLength %s,\n" % float2str(rnd(self.emitter.tail_length)))
        fw("\tTime %s,\n" % float2str(rnd(self.emitter.time)))
        fw("\tSegmentColor {\n")
        fw("\t\tColor {%s, %s, %s},\n" % tuple(map(float2str, reversed(self.emitter.start_color))))
        fw("\t\tColor {%s, %s, %s},\n" % tuple(map(float2str, reversed(self.emitter.mid_color))))
        fw("\t\tColor {%s, %s, %s},\n" % tuple(map(float2str, reversed(self.emitter.end_color))))
        fw("\t},\n")

        alpha = (self.emitter.start_alpha, self.emitter.mid_alpha, self.emitter.end_alpha)
        fw("\tAlpha {%s, %s, %s},\n" % tuple(map(float2str, alpha)))

        particle_scales = (self.emitter.start_scale, self.emitter.mid_scale, self.emitter.end_scale)

        fw("\tParticleScaling {%s, %s, %s},\n" % tuple(map(float2str, particle_scales)))
        fw("\tLifeSpanUVAnim {%d, %d, %d},\n" % (
            self.emitter.head_life_start, self.emitter.head_life_end, self.emitter.head_life_repeat))
        fw("\tDecayUVAnim {%d, %d, %d},\n" % (
            self.emitter.head_decay_start, self.emitter.head_decay_end, self.emitter.head_decay_repeat))
        fw("\tTailUVAnim {%d, %d, %d},\n" % (self.emitter.tail_life_start, self.emitter.tail_life_end, self.emitter.tail_life_repeat))
        fw("\tTailDecayUVAnim {%d, %d, %d},\n" % (
            self.emitter.tail_decay_start, self.emitter.tail_decay_end, self.emitter.tail_decay_repeat))
        fw("\tTextureID %d,\n" % textures.index(self.emitter.texture_path))

        if self.emitter.priority_plane != 0:
            fw("\tPriorityPlane %d,\n" % self.emitter.priority_plane)
        fw("}\n")

    @staticmethod
    def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
        if curve is not None and curve.global_sequence > 0:
            global_seqs.add(curve.global_sequence)
