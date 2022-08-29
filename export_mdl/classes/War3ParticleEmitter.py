from typing import Optional, List, TextIO, Set, Dict

import bpy
from mathutils import Vector

from ..export_mdl.write_animation_chunk import write_animation_chunk
from ..utils import float2str, calc_bounds_radius, rnd
from .War3AnimationAction import War3AnimationAction
from .War3Emitter import War3Emitter
from .War3AnimationCurve import War3AnimationCurve
from .animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve as get_anim
from ..properties import War3ParticleSystemProperties


class War3ParticleEmitter(War3Emitter):
    def __init__(self, name,
                 anim_loc: Optional[War3AnimationCurve],
                 anim_rot: Optional[War3AnimationCurve],
                 anim_scale: Optional[War3AnimationCurve],
                 parent: Optional[str], pivot: Optional):
        super().__init__(name, anim_loc, anim_rot, anim_scale, parent, pivot)
        self.speed_anim: Optional[War3AnimationCurve] = None
        self.variation_anim: Optional[War3AnimationCurve] = None
        self.latitude_anim: Optional[War3AnimationCurve] = None
        self.longitude_anim: Optional[War3AnimationCurve] = None
        self.dimensions: Optional[Vector] = None
        self.scale_anim: Optional[War3AnimationCurve] = None
        self.object_path: str = ""

    def set_from(self, obj: bpy.types.Object, sequences: List[War3AnimationAction], global_seqs: Set[int]):
        settings: bpy.types.ParticleSettings = obj.particle_systems[0].settings

        self.emitter: War3ParticleSystemProperties = settings.mdl_particle_sys
        self.scale_anim: Optional[War3AnimationCurve] = get_anim(obj.animation_data, 'scale', 2, sequences)
        self.register_global_sequence(global_seqs, self.scale_anim)
        # register_global_sequence(model.global_seqs, self.scale_anim)

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
            self.emission_rate_anim = get_anim(bby_anim_data, 'mdl_particle_sys.emission_rate', 1, sequences)
            self.register_global_sequence(global_seqs, self.emission_rate_anim)
            # register_global_sequence(model.global_seqs, self.emission_rate_anim)

            self.speed_anim = get_anim(bby_anim_data, 'mdl_particle_sys.speed', 1, sequences)
            self.register_global_sequence(global_seqs, self.speed_anim)
            # register_global_sequence(model.global_seqs, self.speed_anim)

            self.life_span_anim = get_anim(bby_anim_data, 'mdl_particle_sys.life_span', 1, sequences)
            self.register_global_sequence(global_seqs, self.life_span_anim)
            # register_global_sequence(model.global_seqs, self.life_span_anim)

            self.gravity_anim = get_anim(bby_anim_data, 'mdl_particle_sys.gravity', 1, sequences)
            self.register_global_sequence(global_seqs, self.gravity_anim)
            # register_global_sequence(model.global_seqs, self.gravity_anim)

            self.variation_anim = get_anim(bby_anim_data, 'mdl_particle_sys.variation', 1, sequences)
            self.register_global_sequence(global_seqs, self.variation_anim)
            # register_global_sequence(model.global_seqs, self.variation_anim)

            self.latitude_anim = get_anim(bby_anim_data, 'mdl_particle_sys.latitude', 1, sequences)
            self.register_global_sequence(global_seqs, self.latitude_anim)
            # register_global_sequence(model.global_seqs, self.latitude_anim)

            self.longitude_anim = get_anim(bby_anim_data, 'mdl_particle_sys.longitude', 1, sequences)
            self.register_global_sequence(global_seqs, self.longitude_anim)
            # register_global_sequence(model.global_seqs, self.longitude_anim)

            self.alpha_anim = get_anim(bby_anim_data, 'mdl_particle_sys.alpha', 1, sequences)
            self.register_global_sequence(global_seqs, self.alpha_anim)
            # register_global_sequence(model.global_seqs, self.alpha_anim)

            self.ribbon_color_anim = get_anim(bby_anim_data, 'mdl_particle_sys.ribbon_color', 3, sequences)
            self.register_global_sequence(global_seqs, self.ribbon_color_anim)
            # register_global_sequence(model.global_seqs, self.ribbon_color_anim)

    def write_particle(self, fw: TextIO.write,
                       object_indices: Dict[str, int],
                       global_seqs: Set[int]):
        emitter = self.emitter
        fw("ParticleEmitter \"%s\" {\n" % self.name)
        if len(object_indices) > 1:
            fw("\tObjectId %d,\n" % object_indices[self.name])
        if self.parent is not None:
            fw("\tParent %d,\n" % object_indices[self.parent])

        fw("\tEmitterUsesMDL,\n")

        if self.emission_rate_anim is not None:
            self.write_animated(fw, global_seqs, "EmissionRate", self.emission_rate_anim)
            # write_anim(self.emission_rate_anim, "EmissionRate", fw, global_seqs, "\t")
        else:
            fw("\tstatic EmissionRate %s,\n" % float2str(rnd(emitter.emission_rate)))

        if self.gravity_anim is not None:
            self.write_animated(fw, global_seqs, "Gravity", self.gravity_anim)
            # write_anim(self.gravity_anim, "Gravity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Gravity %s,\n" % float2str(rnd(emitter.gravity)))

        if self.longitude_anim is not None:
            self.write_animated(fw, global_seqs, "Longitude", self.longitude_anim)
            # write_anim(self.longitude_anim, "Longitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Longitude %s,\n" % float2str(rnd(emitter.latitude)))

        if self.latitude_anim is not None:
            self.write_animated(fw, global_seqs, "Latitude", self.latitude_anim)
            # write_anim(self.latitude_anim, "Latitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Latitude %s,\n" % float2str(rnd(emitter.latitude)))

        if self.visibility is not None:
            self.write_animated(fw, global_seqs, "Visibility", self.visibility)
            # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)
        fw("\tParticle {\n")

        if self.life_span_anim is not None:
            self.write_animated(fw, global_seqs, "LifeSpan", self.life_span_anim)
            # write_anim(self.life_span_anim, "LifeSpan", fw, global_seqs, "\t\t")
        else:
            fw("\t\tLifeSpan %s,\n" % float2str(rnd(emitter.life_span)))

        if self.speed_anim is not None:
            self.write_animated(fw, global_seqs, "InitVelocity", self.speed_anim)
            # write_anim(self.speed_anim, "InitVelocity", fw, global_seqs, "\t\t")
        else:
            fw("\t\tstatic InitVelocity %s,\n" % float2str(rnd(emitter.speed)))

        fw("\t\tPath \"%s\",\n" % emitter.model_path)
        fw("\t}\n")
        fw("}\n")

    @staticmethod
    def write_animated(fw: TextIO.write, global_seqs: Set[int], name: str, animation_curve: War3AnimationCurve):
        write_animation_chunk(fw, animation_curve, name, global_seqs, "\t")
        # write_animation_chunk(animation_curve.keyframes, animation_curve.type,
        #                       animation_curve.interpolation, animation_curve.global_sequence,
        #                       animation_curve.handles_left, animation_curve.handles_right,
        #                       name, fw, global_seqs, "\t")

    @staticmethod
    def register_global_sequence(global_seqs: Set[int], curve: Optional[War3AnimationCurve]):
        if curve is not None and curve.global_sequence > 0:
            global_seqs.add(curve.global_sequence)
