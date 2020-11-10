from .War3Object import War3Object
from .War3AnimationCurve import War3AnimationCurve
from .model_utils.register_global_sequence import register_global_sequence


class War3ParticleSystem(War3Object):
    def __init__(self, name, obj, model):
        War3Object.__init__(self, name)

        settings = obj.particle_systems[0].settings

        self.emitter = settings.mdl_particle_sys
        self.scale_anim = War3AnimationCurve.get(obj.animation_data, 'scale', 2, model.sequences)
        register_global_sequence(model.global_seqs, self.scale_anim)

        self.emission_rate_anim = None
        self.speed_anim = None
        self.life_span_anim = None
        self.gravity_anim = None
        self.variation_anim = None
        self.latitude_anim = None
        self.longitude_anim = None
        self.alpha_anim = None
        self.ribbon_color_anim = None

        # Animated properties

        if settings.animation_data is not None:
            self.emission_rate_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.emission_rate', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.emission_rate_anim)

            self.speed_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.speed', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.speed_anim)

            self.life_span_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.life_span', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.life_span_anim)

            self.gravity_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.gravity', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.gravity_anim)

            self.variation_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.variation', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.variation_anim)

            self.latitude_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.latitude', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.latitude_anim)

            self.longitude_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.longitude', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.longitude_anim)

            self.alpha_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.alpha', 1, model.sequences)
            register_global_sequence(model.global_seqs, self.alpha_anim)

            self.ribbon_color_anim = War3AnimationCurve.get(settings.animation_data, 'mdl_particle_sys.ribbon_color', 3, model.sequences)
            register_global_sequence(model.global_seqs, self.ribbon_color_anim)
