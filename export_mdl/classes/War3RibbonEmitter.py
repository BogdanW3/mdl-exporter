from typing import Optional, List, TextIO, Set, Dict

import bpy
from mathutils import Vector

from io_scene_warcraft_3.classes.WarCraft3Texture import WarCraft3Texture
from .War3Material import War3Material
from ..export_mdl.write_animation_chunk import write_animation_chunk
from ..utils import float2str, calc_bounds_radius, rnd
from .War3AnimationAction import War3AnimationAction
from .War3Emitter import War3Emitter
from .War3AnimationCurve import War3AnimationCurve
from .animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve as get_anim
from ..properties import War3ParticleSystemProperties


class War3RibbonEmitter(War3Emitter):
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
        self.ribbon_color_anim: Optional[War3AnimationCurve] = None
        self.dimensions: Optional[Vector] = None
        self.scale_anim: Optional[War3AnimationCurve] = None

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

    def write_ribbon(self, fw: TextIO.write,
                     object_indices: Dict[str, int],
                     global_seqs: Set[int],
                     textures: List[WarCraft3Texture],
                     materials: List[War3Material]):
        emitter = self.emitter
        fw("RibbonEmitter \"%s\" {\n" % self.name)
        if len(object_indices) > 1:
            fw("\tObjectId %d,\n" % object_indices[self.name])
        if self.parent is not None:
            fw("\tParent %d,\n" % object_indices[self.parent])

        fw("\tstatic HeightAbove %s,\n" % float2str(rnd(self.dimensions[0] / 2)))
        fw("\tstatic HeightBelow %s,\n" % float2str(rnd(self.dimensions[0] / 2)))

        if self.alpha_anim is not None:
            self.write_animated(fw, global_seqs, "Alpha", self.alpha_anim)
        else:
            fw("\tstatic Alpha %s,\n" % emitter.alpha)

        if self.ribbon_color_anim is not None:
            self.write_animated(fw, global_seqs, "Color", self.ribbon_color_anim)
            # write_anim_vec(self.ribbon_color_anim, 'Color', 'ribbon_color', fw, global_seqs, Matrix(), Matrix(), "\t", (2, 1, 0))
        else:
            fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(float2str, reversed(emitter.ribbon_color))))

        fw("\tstatic TextureSlot %d,\n" % textures.index(emitter.texture_path))

        if self.visibility is not None:
            self.write_animated(fw, global_seqs, "Visibility", self.visibility)
            # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)

        fw("\tEmissionRate %d,\n" % emitter.emission_rate)
        fw("\tLifeSpan %s,\n" % float2str(rnd(emitter.life_span)))
        fw("\tGravity %s,\n" % float2str(rnd(emitter.gravity)))
        fw("\tRows %d,\n" % emitter.rows)
        fw("\tColumns %d,\n" % emitter.cols)

        for material in materials:
            if material.name == emitter.ribbon_material.name:
                fw("\tMaterialID %d,\n" % materials.index(material))
                break
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
