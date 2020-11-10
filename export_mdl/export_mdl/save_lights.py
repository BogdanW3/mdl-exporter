from export_mdl.export_mdl.write_billboard import write_billboard
from export_mdl.utils import f2s


def save_lights(fw, model):
    for light in model.objects['light']:
        l = light.object
        fw("Light \"%s\" {\n" % light.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[light.name])

        if light.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[light.parent])

        write_billboard(fw, light.billboarded, light.billboard_lock)

        fw("\t%s,\n" % light.type)

        if light.atten_start_anim is not None:
            light.atten_start_anim.write_mdl("AttenuationStart", fw, model.global_seqs,
                                             "\t")  # write_anim(light.atten_start_anim, "AttenuationStart", fw, global_seqs, "\t")
        else:
            fw("\tstatic AttenuationStart %s,\n" % f2s(light.atten_start))

        if light.atten_end_anim is not None:
            light.atten_end_anim.write_mdl("AttenuationEnd", fw, model.global_seqs,
                                           "\t")  # write_anim(light.atten_end_anim, "AttenuationEnd", fw, global_seqs, "\t")
        else:
            fw("\tstatic AttenuationEnd %s,\n" % f2s(light.atten_end))  # TODO: Add animation support

        if light.color_anim is not None:
            light.color_anim.write_mdl("Color", fw, model.global_seqs,
                                       "\t")  # write_anim_vec(light.color_anim, "Color", 'color', fw, global_seqs, Matrix(), Matrix())
        else:
            fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(f2s, reversed(light.color[:3]))))

        if light.intensity_anim is not None:
            light.intensity_anim.write_mdl("Intensity", fw, model.global_seqs,
                                           "\t")  # write_anim(light.intensity_anim, "Intensity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Intensity %s,\n" % f2s(light.intensity))

        if light.amb_intensity_anim is not None:
            light.amb_intensity_anim.write_mdl("AmbIntensity", fw, model.global_seqs,
                                               "\t")  # write_anim(light.amb_intensity_anim, "AmbIntensity", fw, global_seqs, "\t")
        else:
            fw("\tstatic AmbIntensity %s,\n" % f2s(light.amb_intensity))

        if light.amb_color_anim is not None:
            light.amb_color_anim.write_mdl("AmbColor", fw, model.global_seqs,
                                           "\t")  # write_anim_vec(light.amb_color_anim, "Color", 'color', fw, global_seqs, Matrix(), Matrix())
        else:
            fw("\tstatic AmbColor {%s, %s, %s},\n" % tuple(map(f2s, reversed(light.amb_color[:3]))))

        if light.visibility is not None:
            light.visibility.write_mdl("Visibility", fw, model.global_seqs,
                                       "\t")  # write_anim(light.visibility, "Visibility", fw, global_seqs, "\t", True)
        fw("}\n")