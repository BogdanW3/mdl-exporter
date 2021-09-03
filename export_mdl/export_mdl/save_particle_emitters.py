from typing import TextIO

from .write_mdl import write_mdl
from ..classes.War3Model import War3Model
from ..utils import f2s, rnd


def save_particle_emitters(fw: TextIO.write, model: War3Model):
    for psys in model.objects['particle2']:
        emitter = psys.emitter
        fw("ParticleEmitter2 \"%s\" {\n" % psys.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[psys.name])
        if psys.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[psys.parent])

        if emitter.sort_far_z:
            fw("\tSortPrimsFarZ,\n")

        if emitter.unshaded:
            fw("\tUnshaded,\n")

        if emitter.line_emitter:
            fw("\tLineEmitter,\n")

        if emitter.unfogged:
            fw("\tUnfogged,\n")

        if emitter.model_space:
            fw("\tModelSpace,\n")

        if emitter.xy_quad:
            fw("\tXYQuad,\n")

        if psys.speed_anim is not None:
            write_mdl(psys.speed_anim.keyframes, psys.speed_anim.type,
                      psys.speed_anim.interpolation, psys.speed_anim.global_sequence,
                      psys.speed_anim.handles_left, psys.speed_anim.handles_right,
                      "Speed", fw, model.global_seqs, "\t")
            # write_anim(psys.speed_anim, "Speed", fw, global_seqs, "\t")
        else:
            fw("\tstatic Speed %s,\n" % f2s(rnd(emitter.speed)))

        if psys.variation_anim is not None:
            write_mdl(psys.variation_anim.keyframes, psys.variation_anim.type,
                      psys.variation_anim.interpolation, psys.variation_anim.global_sequence,
                      psys.variation_anim.handles_left, psys.variation_anim.handles_right,
                      "Variation", fw, model.global_seqs, "\t")
            # write_anim(psys.variation_anim, "Variation", fw, global_seqs, "\t")
        else:
            fw("\tstatic Variation %s,\n" % f2s(rnd(emitter.variation)))

        if psys.latitude_anim is not None:
            write_mdl(psys.latitude_anim.keyframes, psys.latitude_anim.type,
                      psys.latitude_anim.interpolation, psys.latitude_anim.global_sequence,
                      psys.latitude_anim.handles_left, psys.latitude_anim.handles_right,
                      "Latitude", fw, model.global_seqs, "\t")
            # write_anim(psys.latitude_anim, "Latitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Latitude %s,\n" % f2s(rnd(emitter.latitude)))

        if psys.gravity_anim is not None:
            write_mdl(psys.gravity_anim.keyframes, psys.gravity_anim.type,
                      psys.gravity_anim.interpolation, psys.gravity_anim.global_sequence,
                      psys.gravity_anim.handles_left, psys.gravity_anim.handles_right,
                      "Gravity", fw, model.global_seqs, "\t")
            # write_anim(psys.gravity_anim, "Gravity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Gravity %s,\n" % f2s(rnd(emitter.gravity)))

        visibility = psys.visibility
        if visibility is not None:
            write_mdl(visibility.keyframes, visibility.type,
                      visibility.interpolation, visibility.global_sequence,
                      visibility.handles_left, visibility.handles_right,
                      "Visibility", fw, model.global_seqs, "\t")
            # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)

        fw("\tLifeSpan %s,\n" % f2s(rnd(emitter.life_span)))

        if psys.emission_rate_anim is not None:
            write_mdl(psys.emission_rate_anim.keyframes, psys.emission_rate_anim.type,
                      psys.emission_rate_anim.interpolation, psys.emission_rate_anim.global_sequence,
                      psys.emission_rate_anim.handles_left, psys.emission_rate_anim.handles_right,
                      "EmissionRate", fw, model.global_seqs, "\t")
            # write_anim(psys.emission_rate_anim, "EmissionRate", fw, global_seqs, "\t")
        else:
            fw("\tstatic EmissionRate %s,\n" % f2s(rnd(emitter.emission_rate)))

        # FIXME FIXME FIXME FIXME FIXME: Separate X and Y channels! New animation class won't handle this.
        if psys.scale_anim is not None and ('scale', 1) in psys.scale_anim.keys():
            write_mdl(psys.scale_anim.keyframes, psys.scale_anim.type,
                      psys.scale_anim.interpolation, psys.scale_anim.global_sequence,
                      psys.scale_anim.handles_left, psys.scale_anim.handles_right,
                      "Width", fw, model.global_seqs, "\t")
            # write_anim(psys.scale_anim[('scale', 1)], "Width", fw, global_seqs, "\t", scale=psys.dimensions[1])
        else:
            fw("\tstatic Width %s,\n" % f2s(rnd(psys.dimensions[1])))

        if psys.scale_anim is not None and ('scale', 0) in psys.scale_anim.keys():
            write_mdl(psys.scale_anim.keyframes, psys.scale_anim.type,
                      psys.scale_anim.interpolation, psys.scale_anim.global_sequence,
                      psys.scale_anim.handles_left, psys.scale_anim.handles_right,
                      "Length", fw, model.global_seqs, "\t")
            # write_anim(psys.scale_anim[('scale', 0)], "Length", fw, global_seqs, "\t", scale=psys.dimensions[0])
        else:
            fw("\tstatic Length %s,\n" % f2s(rnd(psys.dimensions[0])))

        fw("\t%s,\n" % emitter.filter_mode)
        fw("\tRows %d,\n" % emitter.rows)
        fw("\tColumns %d,\n" % emitter.cols)

        if emitter.head and emitter.tail:
            fw("\tBoth,\n")
        elif emitter.tail:
            fw("\tTail,\n")
        else:
            fw("\tHead,\n")

        fw("\tTailLength %s,\n" % f2s(rnd(emitter.tail_length)))
        fw("\tTime %s,\n" % f2s(rnd(emitter.time)))
        fw("\tSegmentColor {\n")
        fw("\t\tColor {%s, %s, %s},\n" % tuple(map(f2s, reversed(emitter.start_color))))
        fw("\t\tColor {%s, %s, %s},\n" % tuple(map(f2s, reversed(emitter.mid_color))))
        fw("\t\tColor {%s, %s, %s},\n" % tuple(map(f2s, reversed(emitter.end_color))))
        fw("\t},\n")

        alpha = (emitter.start_alpha, emitter.mid_alpha, emitter.end_alpha)
        fw("\tAlpha {%s, %s, %s},\n" % tuple(map(f2s, alpha)))

        particle_scales = (emitter.start_scale, emitter.mid_scale, emitter.end_scale)

        fw("\tParticleScaling {%s, %s, %s},\n" % tuple(map(f2s, particle_scales)))
        fw("\tLifeSpanUVAnim {%d, %d, %d},\n" % (emitter.head_life_start, emitter.head_life_end, emitter.head_life_repeat))
        fw("\tDecayUVAnim {%d, %d, %d},\n" % (emitter.head_decay_start, emitter.head_decay_end, emitter.head_decay_repeat))
        fw("\tTailUVAnim {%d, %d, %d},\n" % ( emitter.tail_life_start, emitter.tail_life_end, emitter.tail_life_repeat))
        fw("\tTailDecayUVAnim {%d, %d, %d},\n" % (emitter.tail_decay_start, emitter.tail_decay_end, emitter.tail_decay_repeat))
        fw("\tTextureID %d,\n" % model.textures.index(emitter.texture_path))

        if emitter.priority_plane != 0:
            fw("\tPriorityPlane %d,\n" % emitter.priority_plane)
        fw("}\n")
