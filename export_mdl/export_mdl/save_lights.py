from typing import TextIO, Set

from .write_billboard import write_billboard
from .write_animation_chunk import write_animation_chunk
from ..classes.War3AnimationCurve import War3AnimationCurve
from ..classes.War3Model import War3Model
from ..utils import float2str


def save_lights(fw: TextIO.write, model: War3Model):
    for light in model.lights:
        fw("Light \"%s\" {\n" % light.name)
        if 0 <= light.obj_id:
            fw("\tObjectId %d,\n" % light.obj_id)

        if light.parent_id is not None:
            fw("\tParent %d,\n" % light.parent_id)

        write_billboard(fw, light.billboarded, light.billboard_lock)

        fw("\t%s,\n" % light.light_type)

        global_seqs = model.global_seqs
        if light.atten_start_anim is not None:
            write_animated(fw, global_seqs, "AttenuationStart", light.atten_start_anim)
        else:
            fw("\tstatic AttenuationStart %s,\n" % float2str(light.atten_start))

        if light.atten_end_anim is not None:
            write_animated(fw, global_seqs, "AttenuationEnd", light.atten_end_anim)
        else:
            fw("\tstatic AttenuationEnd %s,\n" % float2str(light.atten_end))  # TODO: Add animation support

        if light.color_anim is not None:
            write_animated(fw, global_seqs, "Color", light.color_anim)
        else:
            fw("\tstatic Color { %s, %s, %s },\n" % tuple(map(float2str, reversed(light.color[:3]))))

        if light.intensity_anim is not None:
            write_animated(fw, global_seqs, "Intensity", light.intensity_anim)
        else:
            fw("\tstatic Intensity %s,\n" % float2str(light.intensity))

        if light.amb_intensity_anim is not None:
            write_animated(fw, global_seqs, "AmbIntensity", light.amb_intensity_anim)
        else:
            fw("\tstatic AmbIntensity %s,\n" % float2str(light.amb_intensity))

        if light.amb_color_anim is not None:
            write_animated(fw, global_seqs, "AmbColor", light.amb_color_anim)
        else:
            fw("\tstatic AmbColor { %s, %s, %s },\n" % tuple(map(float2str, reversed(light.amb_color[:3]))))

        visibility = light.visibility
        if visibility is not None:
            name = "Visibility"
            write_animated(fw, global_seqs, name, visibility)
        fw("}\n")


def write_animated(fw: TextIO.write, global_seqs: Set[int], name: str, visibility: War3AnimationCurve):
    write_animation_chunk(fw, visibility, name, global_seqs, "\t")
    # write_animation_chunk(visibility.keyframes, visibility.type,
    #                       visibility.interpolation, visibility.global_sequence,
    #                       visibility.handles_left, visibility.handles_right,
    #                       name, fw, global_seqs, "\t")
