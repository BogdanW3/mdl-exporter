from export_mdl.utils import f2s, rnd


def save_model_emitters(fw, model):
    for psys in model.objects['particle']:
        emitter = psys.emitter
        fw("ParticleEmitter \"%s\" {\n" % psys.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[psys.name])
        if psys.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[psys.parent])

        fw("\tEmitterUsesMDL,\n")

        if psys.emission_rate_anim is not None:
            psys.emission_rate_anim.write_mdl("EmissionRate", fw, model.global_seqs,
                                              "\t")  # write_anim(psys.emission_rate_anim, "EmissionRate", fw, global_seqs, "\t")
        else:
            fw("\tstatic EmissionRate %s,\n" % f2s(rnd(emitter.emission_rate)))

        if psys.gravity_anim is not None:
            psys.gravity_anim.write_mdl("Gravity", fw, model.global_seqs,
                                        "\t")  # write_anim(psys.gravity_anim, "Gravity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Gravity %s,\n" % f2s(rnd(emitter.gravity)))

        if psys.longitude_anim is not None:
            psys.longitude_anim.write_mdl("Longitude", fw, model.global_seqs,
                                          "\t")  # write_anim(psys.longitude_anim, "Longitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Longitude %s,\n" % f2s(rnd(emitter.latitude)))

        if psys.latitude_anim is not None:
            psys.latitude_anim.write_mdl("Latitude", fw, model.global_seqs,
                                         "\t")  # write_anim(psys.latitude_anim, "Latitude", fw, global_seqs, "\t")
        else:
            fw("\tstatic Latitude %s,\n" % f2s(rnd(emitter.latitude)))

        visibility = psys.visibility
        if visibility is not None:
            visibility.write_mdl("Visibility", fw, model.global_seqs,
                                 "\t")  # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)
        fw("\tParticle {\n")

        if psys.life_span_anim is not None:
            psys.life_span_anim.write_mdl("LifeSpan", fw, model.global_seqs,
                                          "\t")  # write_anim(psys.life_span_anim, "LifeSpan", fw, global_seqs, "\t\t")
        else:
            fw("\t\tLifeSpan %s,\n" % f2s(rnd(emitter.life_span)))

        if psys.speed_anim is not None:
            psys.speed_anim.write_mdl("InitVelocity", fw, model.global_seqs,
                                      "\t")  # write_anim(psys.speed_anim, "InitVelocity", fw, global_seqs, "\t\t")
        else:
            fw("\t\tstatic InitVelocity %s,\n" % f2s(rnd(emitter.speed)))

        fw("\t\tPath \"%s\",\n" % emitter.model_path)
        fw("\t}\n")
        fw("}\n")