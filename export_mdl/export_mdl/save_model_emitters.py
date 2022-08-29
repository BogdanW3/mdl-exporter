from typing import TextIO, List, Dict, Set

from .write_animation_chunk import write_animation_chunk
from ..classes.War3ParticleEmitter import War3ParticleEmitter
from ..utils import float2str, rnd


def save_model_emitters(fw: TextIO.write, particle_systems: List[War3ParticleEmitter],
                        object_indices: Dict[str, int], global_seqs: Set[int]):
    for psys in particle_systems:
        psys.write_particle(fw, object_indices, global_seqs)
        # emitter = psys.emitter
        # fw("ParticleEmitter \"%s\" {\n" % psys.name)
        # if len(object_indices) > 1:
        #     fw("\tObjectId %d,\n" % object_indices[psys.name])
        # if psys.parent is not None:
        #     fw("\tParent %d,\n" % object_indices[psys.parent])
        #
        # fw("\tEmitterUsesMDL,\n")
        #
        # anim = psys.emission_rate_anim
        # if anim is not None:
        #     write_animated(fw, global_seqs, "EmissionRate", anim)
        #     # write_anim(psys.emission_rate_anim, "EmissionRate", fw, global_seqs, "\t")
        # else:
        #     fw("\tstatic EmissionRate %s,\n" % float2str(rnd(emitter.emission_rate)))
        #
        # gravity_anim = psys.gravity_anim
        # if gravity_anim is not None:
        #     write_animated(fw, global_seqs, "Gravity", gravity_anim)
        #     # write_anim(psys.gravity_anim, "Gravity", fw, global_seqs, "\t")
        # else:
        #     fw("\tstatic Gravity %s,\n" % float2str(rnd(emitter.gravity)))
        #
        # longitude_anim = psys.longitude_anim
        # if longitude_anim is not None:
        #     write_animated(fw, global_seqs, "Longitude", longitude_anim)
        #     # write_anim(psys.longitude_anim, "Longitude", fw, global_seqs, "\t")
        # else:
        #     fw("\tstatic Longitude %s,\n" % float2str(rnd(emitter.latitude)))
        #
        # latitude_anim = psys.latitude_anim
        # if latitude_anim is not None:
        #     write_animated(fw, global_seqs, "Latitude", latitude_anim)
        #     # write_anim(psys.latitude_anim, "Latitude", fw, global_seqs, "\t")
        # else:
        #     fw("\tstatic Latitude %s,\n" % float2str(rnd(emitter.latitude)))
        #
        # visibility = psys.visibility
        # if visibility is not None:
        #     write_animated(fw, global_seqs, "Visibility", visibility)
        #     # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)
        # fw("\tParticle {\n")
        #
        # life_span_anim = psys.life_span_anim
        # if life_span_anim is not None:
        #     write_animated(fw, global_seqs, "LifeSpan", life_span_anim)
        #     # write_anim(psys.life_span_anim, "LifeSpan", fw, global_seqs, "\t\t")
        # else:
        #     fw("\t\tLifeSpan %s,\n" % float2str(rnd(emitter.life_span)))
        #
        # speed_anim = psys.speed_anim
        # if speed_anim is not None:
        #     write_animated(fw, global_seqs, "InitVelocity", speed_anim)
        #     # write_anim(psys.speed_anim, "InitVelocity", fw, global_seqs, "\t\t")
        # else:
        #     fw("\t\tstatic InitVelocity %s,\n" % float2str(rnd(emitter.speed)))
        #
        # fw("\t\tPath \"%s\",\n" % emitter.model_path)
        # fw("\t}\n")
        # fw("}\n")


def write_animated(fw, global_seqs, name, speed_anim):
    write_animation_chunk(fw, speed_anim, name, global_seqs, "\t")
    # write_animation_chunk(speed_anim.keyframes, speed_anim.type,
    #                       speed_anim.interpolation, speed_anim.global_sequence,
    #                       speed_anim.handles_left, speed_anim.handles_right,
    #                       name, fw, global_seqs, "\t")
