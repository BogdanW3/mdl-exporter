from typing import Optional, List, TextIO, Set, Dict

import bpy
from mathutils import Vector, Matrix

from .War3Texture import War3Texture
from ..export_mdl.write_animation_chunk import write_animation_chunk
from ..utils import float2str, rnd
from .War3AnimationAction import War3AnimationAction
from .War3Node import War3Node
from .War3Emitter import War3Emitter
from .War3AnimationCurve import War3AnimationCurve
from .animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from ..properties import War3ParticleSystemProperties


class War3ParticleSystem(War3Emitter):
    def __init__(self, name,
                 obj_id: int = 0,
                 pivot: List[float] = [0, 0, 0],
                 parent_id: Optional[int] = None,
                 parent: Optional[str] = None,
                 anim_loc: Optional[War3AnimationCurve] = None,
                 anim_rot: Optional[War3AnimationCurve] = None,
                 anim_scale: Optional[War3AnimationCurve] = None,
                 bindpose: Optional[Matrix] = None):
        super().__init__(name, obj_id, pivot, parent_id, parent, anim_loc, anim_rot, anim_scale, bindpose)
        self.emission_rate_anim: Optional[War3AnimationCurve] = None
        self.speed_anim: Optional[War3AnimationCurve] = None
        self.life_span_anim: Optional[War3AnimationCurve] = None
        self.gravity_anim: Optional[War3AnimationCurve] = None
        self.variation_anim: Optional[War3AnimationCurve] = None
        self.latitude_anim: Optional[War3AnimationCurve] = None
        self.longitude_anim: Optional[War3AnimationCurve] = None
        self.alpha_anim: Optional[War3AnimationCurve] = None
        self.ribbon_color_anim: Optional[War3AnimationCurve] = None
        Vector()
        self.emitter: War3ParticleSystemProperties = None
        self.dimensions: Optional[Vector] = None
        self.scale_anim: Optional[War3AnimationCurve] = None

    @classmethod
    def create_from(cls, node: 'War3Node'):
        return War3ParticleSystem(node.name, node.obj_id, node.pivot,
                                  node.parent_id, node.parent,
                                  node.anim_loc, node.anim_rot, node.anim_scale,
                                  node.bindpose)

    def set_from(self, obj: bpy.types.Object, actions: List[bpy.types.Action], sequences: List[War3AnimationAction], global_seqs: Set[int]):
        settings: bpy.types.ParticleSettings = obj.particle_systems[0].settings

        self.emitter: War3ParticleSystemProperties = settings.mdl_particle_sys
        self.scale_anim: Optional[War3AnimationCurve] = self.anim_stuff(obj.animation_data, actions, 'scale', 2, sequences, global_seqs)

        # Animated properties
        bby_anim_data = settings.animation_data
        if bby_anim_data is None:
            self.emission_rate_anim: Optional[War3AnimationCurve] = None
            self.speed_anim: Optional[War3AnimationCurve] = None
            self.life_span_anim: Optional[War3AnimationCurve] = None
            self.gravity_anim: Optional[War3AnimationCurve] = None
            self.variation_anim: Optional[War3AnimationCurve] = None
            self.latitude_anim: Optional[War3AnimationCurve] = None
            self.longitude_anim: Optional[War3AnimationCurve] = None
            self.alpha_anim: Optional[War3AnimationCurve] = None
            self.ribbon_color_anim: Optional[War3AnimationCurve] = None
        else:
            self.emission_rate_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.emission_rate', 1, sequences, global_seqs)

            self.speed_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.speed', 1, sequences, global_seqs)

            self.life_span_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.life_span', 1, sequences, global_seqs)

            self.gravity_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.gravity', 1, sequences, global_seqs)

            self.variation_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.variation', 1, sequences, global_seqs)

            self.latitude_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.latitude', 1, sequences, global_seqs)

            self.longitude_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.longitude', 1, sequences, global_seqs)

            self.alpha_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.alpha', 1, sequences, global_seqs)

            self.ribbon_color_anim = self.anim_stuff(bby_anim_data, actions, 'mdl_particle_sys.ribbon_color', 3, sequences, global_seqs)

    def anim_stuff(self, animation_data: Optional[bpy.types.AnimData], actions: List[bpy.types.Action], data_path: str, num_indices: int,
                   sequences: List[War3AnimationAction], global_seqs: Set[int]):
        curve = get_wc3_animation_curve(data_path, actions, num_indices, sequences, global_seqs)
        return curve

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
            War3ParticleSystem.write_animated(fw, self.speed_anim, global_seqs, "Speed")
            # write_anim(self.speed_anim, "Speed", fw, global_seqs, "\t")
        else:
            fw("\tstatic Speed %s,\n" % float2str(rnd(self.emitter.speed)))

        if self.variation_anim is not None:
            War3ParticleSystem.write_animated(fw, self.variation_anim, global_seqs, "Variation")
            # write_anim(self.variation_anim, "Variation", fw, global_seqs, "\t")
        else:
            fw("\tstatic Variation %s,\n" % float2str(rnd(self.emitter.variation)))

        if self.latitude_anim is not None:
            War3ParticleSystem.write_animated(fw, self.latitude_anim, global_seqs, "Latitude")
            # write_anim(self.latitude_anim, "Latitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Latitude %s,\n" % float2str(rnd(self.emitter.latitude)))

        if self.gravity_anim is not None:
            War3ParticleSystem.write_animated(fw, self.gravity_anim, global_seqs, "Gravity")
            # write_anim(self.gravity_anim, "Gravity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Gravity %s,\n" % float2str(rnd(self.emitter.gravity)))

        visibility = self.visibility
        if visibility is not None:
            War3ParticleSystem.write_animated(fw, visibility, global_seqs, "Visibility")
            # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)

        fw("\tLifeSpan %s,\n" % float2str(rnd(self.emitter.life_span)))

        if self.emission_rate_anim is not None:
            War3ParticleSystem.write_animated(fw, self.emission_rate_anim, global_seqs, "EmissionRate")
            # write_anim(self.emission_rate_anim, "EmissionRate", fw, global_seqs, "\t")
        else:
            fw("\tstatic EmissionRate %s,\n" % float2str(rnd(self.emitter.emission_rate)))

        # FIXME FIXME FIXME FIXME FIXME: Separate X and Y channels! New animation class won't handle this.
        if self.scale_anim is not None and ('scale', 1) in self.scale_anim.keys():
            War3ParticleSystem.write_animated(fw, self.scale_anim, global_seqs, "Width")
            # write_anim(self.scale_anim[('scale', 1)], "Width", fw, global_seqs, "\t", scale=self.dimensions[1])
        else:
            fw("\tstatic Width %s,\n" % float2str(rnd(self.dimensions[1])))

        if self.scale_anim is not None and ('scale', 0) in self.scale_anim.keys():
            War3ParticleSystem.write_animated(fw, self.scale_anim, global_seqs, "Length")
            # write_anim(self.scale_anim[('scale', 0)], "Length", fw, global_seqs, "\t", scale=self.dimensions[0])
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
        fw("\t\tColor { %s, %s, %s },\n" % tuple(map(float2str, reversed(self.emitter.start_color))))
        fw("\t\tColor { %s, %s, %s },\n" % tuple(map(float2str, reversed(self.emitter.mid_color))))
        fw("\t\tColor { %s, %s, %s },\n" % tuple(map(float2str, reversed(self.emitter.end_color))))
        fw("\t},\n")

        alpha = (self.emitter.start_alpha, self.emitter.mid_alpha, self.emitter.end_alpha)
        fw("\tAlpha { %s, %s, %s },\n" % tuple(map(float2str, alpha)))

        particle_scales = (self.emitter.start_scale, self.emitter.mid_scale, self.emitter.end_scale)

        fw("\tParticleScaling { %s, %s, %s },\n" % tuple(map(float2str, particle_scales)))
        fw("\tLifeSpanUVAnim { %d, %d, %d },\n" % (self.emitter.head_life_start, self.emitter.head_life_end, self.emitter.head_life_repeat))
        fw("\tDecayUVAnim { %d, %d, %d },\n" % (self.emitter.head_decay_start, self.emitter.head_decay_end, self.emitter.head_decay_repeat))
        fw("\tTailUVAnim { %d, %d, %d },\n" % (self.emitter.tail_life_start, self.emitter.tail_life_end, self.emitter.tail_life_repeat))
        fw("\tTailDecayUVAnim { %d, %d, %d },\n" % (self.emitter.tail_decay_start, self.emitter.tail_decay_end, self.emitter.tail_decay_repeat))
        fw("\tTextureID %d,\n" % textures.index(self.emitter.texture_path))

        if self.emitter.priority_plane != 0:
            fw("\tPriorityPlane %d,\n" % self.emitter.priority_plane)
        fw("}\n")

    @staticmethod
    def write_animated(fw: TextIO.write, animation_curve: War3AnimationCurve, global_seqs: Set[int], name: str):
        write_animation_chunk(fw, animation_curve, name, global_seqs, "\t")
        # write_animation_chunk(animation_curve.keyframes, animation_curve.type,
        #                       animation_curve.interpolation, animation_curve.global_sequence,
        #                       animation_curve.handles_left, animation_curve.handles_right,
        #                       name, fw, global_seqs, "\t")


    @staticmethod
    def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
        if curve is not None and curve.global_sequence > 0:
            global_seqs.add(curve.global_sequence)
