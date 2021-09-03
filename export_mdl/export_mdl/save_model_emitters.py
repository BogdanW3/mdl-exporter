from typing import TextIO

from .write_mdl import write_mdl
from ..classes.War3Model import War3Model
from ..utils import f2s, rnd


def save_model_emitters(fw: TextIO.write, model: War3Model):
    for psys in model.objects['particle']:
        emitter = psys.emitter
        fw("ParticleEmitter \"%s\" {\n" % psys.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[psys.name])
        if psys.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[psys.parent])

        fw("\tEmitterUsesMDL,\n")

        if psys.emission_rate_anim is not None:
            write_mdl(psys.emission_rate_anim.keyframes, psys.emission_rate_anim.type,
                      psys.emission_rate_anim.interpolation, psys.emission_rate_anim.global_sequence,
                      psys.emission_rate_anim.handles_left, psys.emission_rate_anim.handles_right,
                      "EmissionRate", fw, model.global_seqs, "\t")
            # write_anim(psys.emission_rate_anim, "EmissionRate", fw, global_seqs, "\t")
        else:
            fw("\tstatic EmissionRate %s,\n" % f2s(rnd(emitter.emission_rate)))

        if psys.gravity_anim is not None:
            write_mdl(psys.gravity_anim.keyframes, psys.gravity_anim.type,
                      psys.gravity_anim.interpolation, psys.gravity_anim.global_sequence,
                      psys.gravity_anim.handles_left, psys.gravity_anim.handles_right,
                      "Gravity", fw, model.global_seqs, "\t")
            # write_anim(psys.gravity_anim, "Gravity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Gravity %s,\n" % f2s(rnd(emitter.gravity)))

        if psys.longitude_anim is not None:
            write_mdl(psys.longitude_anim.keyframes, psys.longitude_anim.type,
                      psys.longitude_anim.interpolation, psys.longitude_anim.global_sequence,
                      psys.longitude_anim.handles_left, psys.longitude_anim.handles_right,
                      "Longitude", fw, model.global_seqs, "\t")
            # write_anim(psys.longitude_anim, "Longitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Longitude %s,\n" % f2s(rnd(emitter.latitude)))

        if psys.latitude_anim is not None:
            write_mdl(psys.latitude_anim.keyframes, psys.latitude_anim.type,
                      psys.latitude_anim.interpolation, psys.latitude_anim.global_sequence,
                      psys.latitude_anim.handles_left, psys.latitude_anim.handles_right,
                      "Latitude", fw, model.global_seqs, "\t")
            # write_anim(psys.latitude_anim, "Latitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Latitude %s,\n" % f2s(rnd(emitter.latitude)))

        visibility = psys.visibility
        if visibility is not None:
            write_mdl(visibility.keyframes, visibility.type,
                      visibility.interpolation, visibility.global_sequence,
                      visibility.handles_left, visibility.handles_right,
                      "Visibility", fw, model.global_seqs, "\t")
            # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)
        fw("\tParticle {\n")

        if psys.life_span_anim is not None:
            write_mdl(psys.life_span_anim.keyframes, psys.life_span_anim.type,
                      psys.life_span_anim.interpolation, psys.life_span_anim.global_sequence,
                      psys.life_span_anim.handles_left, psys.life_span_anim.handles_right,
                      "LifeSpan", fw, model.global_seqs, "\t")
            # write_anim(psys.life_span_anim, "LifeSpan", fw, global_seqs, "\t\t")
        else:
            fw("\t\tLifeSpan %s,\n" % f2s(rnd(emitter.life_span)))

        if psys.speed_anim is not None:
            write_mdl(psys.speed_anim.keyframes, psys.speed_anim.type,
                      psys.speed_anim.interpolation, psys.speed_anim.global_sequence,
                      psys.speed_anim.handles_left, psys.speed_anim.handles_right,
                      "InitVelocity", fw, model.global_seqs, "\t")
            # write_anim(psys.speed_anim, "InitVelocity", fw, global_seqs, "\t\t")
        else:
            fw("\t\tstatic InitVelocity %s,\n" % f2s(rnd(emitter.speed)))

        fw("\t\tPath \"%s\",\n" % emitter.model_path)
        fw("\t}\n")
        fw("}\n")
