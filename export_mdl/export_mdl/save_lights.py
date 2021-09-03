from typing import TextIO

from .write_billboard import write_billboard
from .write_mdl import write_mdl
from ..classes.War3Model import War3Model
from ..utils import f2s


def save_lights(fw: TextIO.write, model: War3Model):
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
            write_mdl(light.atten_start_anim.keyframes, light.atten_start_anim.type,
                      light.atten_start_anim.interpolation, light.atten_start_anim.global_sequence,
                      light.atten_start_anim.handles_left, light.atten_start_anim.handles_right,
                      "AttenuationStart", fw, model.global_seqs, "\t")
            # write_anim(light.atten_start_anim, "AttenuationStart", fw, global_seqs, "\t")
        else:
            fw("\tstatic AttenuationStart %s,\n" % f2s(light.atten_start))

        if light.atten_end_anim is not None:
            write_mdl(light.atten_end_anim.keyframes, light.atten_end_anim.type,
                      light.atten_end_anim.interpolation, light.atten_end_anim.global_sequence,
                      light.atten_end_anim.handles_left, light.atten_end_anim.handles_right,
                      "AttenuationEnd",  fw, model.global_seqs, "\t")
            # write_anim(light.atten_end_anim, "AttenuationEnd", fw, global_seqs, "\t")
        else:
            fw("\tstatic AttenuationEnd %s,\n" % f2s(light.atten_end))  # TODO: Add animation support

        if light.color_anim is not None:
            write_mdl(light.color_anim.keyframes, light.color_anim.type,
                      light.color_anim.interpolation, light.color_anim.global_sequence,
                      light.color_anim.handles_left, light.color_anim.handles_right,
                      "Color", fw, model.global_seqs, "\t")
            # write_anim_vec(light.color_anim, "Color", 'color', fw, global_seqs, Matrix(), Matrix())
        else:
            fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(f2s, reversed(light.color[:3]))))

        if light.intensity_anim is not None:
            write_mdl(light.intensity_anim.keyframes, light.intensity_anim.type,
                      light.intensity_anim.interpolation, light.intensity_anim.global_sequence,
                      light.intensity_anim.handles_left, light.intensity_anim.handles_right,
                      "Intensity", fw, model.global_seqs, "\t")
            # write_anim(light.intensity_anim, "Intensity", fw, global_seqs, "\t")
        else:
            fw("\tstatic Intensity %s,\n" % f2s(light.intensity))

        if light.amb_intensity_anim is not None:
            write_mdl(light.amb_intensity_anim.keyframes, light.amb_intensity_anim.type,
                      light.amb_intensity_anim.interpolation, light.amb_intensity_anim.global_sequence,
                      light.amb_intensity_anim.handles_left, light.amb_intensity_anim.handles_right,
                      "AmbIntensity", fw, model.global_seqs, "\t")
            # write_anim(light.amb_intensity_anim, "AmbIntensity", fw, global_seqs, "\t")
        else:
            fw("\tstatic AmbIntensity %s,\n" % f2s(light.amb_intensity))

        if light.amb_color_anim is not None:
            write_mdl(light.amb_color_anim.keyframes, light.amb_color_anim.type,
                      light.amb_color_anim.interpolation, light.amb_color_anim.global_sequence,
                      light.amb_color_anim.handles_left, light.amb_color_anim.handles_right,
                      "AmbColor", fw, model.global_seqs, "\t")
            # write_anim_vec(light.amb_color_anim, "Color", 'color', fw, global_seqs, Matrix(), Matrix())
        else:
            fw("\tstatic AmbColor {%s, %s, %s},\n" % tuple(map(f2s, reversed(light.amb_color[:3]))))

        if light.visibility is not None:
            write_mdl(light.visibility.keyframes, light.visibility.type,
                      light.visibility.interpolation, light.visibility.global_sequence,
                      light.visibility.handles_left, light.visibility.handles_right,
                      "Visibility", fw, model.global_seqs, "\t")
            # write_anim(light.visibility, "Visibility", fw, global_seqs, "\t", True)
        fw("}\n")
