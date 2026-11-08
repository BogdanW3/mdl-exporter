from typing import TextIO, Set

from .write_billboard import write_billboard
from .write_animation_chunk import write_animation_chunk
from ..classes.War3AnimationCurve import War3AnimationCurve
from ..classes.War3Model import War3Model
from ..utils import float2str


def save_lights(fw: TextIO.write, model: War3Model, version: int = 800):
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

        if version >= 1200 and light.shadow_intensity is not None:
            fw("\tstatic ShadowIntensity %s,\n" % float2str(light.shadow_intensity))

        if version >= 1300:
            if light.shadow_casting:
                fw("\tShadowCasting,\n")
            write_static_or_animated(fw, global_seqs, "ShadowCastingStart", light.shadow_casting_start, light.shadow_casting_start_anim)
            write_static_or_animated(fw, global_seqs, "ShadowCastingEnd", light.shadow_casting_end, light.shadow_casting_end_anim)

        if version >= 1600:
            write_static_or_animated(fw, global_seqs, "QuadraticFalloff", light.quadratic_falloff, light.quadratic_falloff_anim)
            write_static_or_animated(fw, global_seqs, "LinearFalloff", light.linear_falloff, light.linear_falloff_anim)
            write_static_or_animated(fw, global_seqs, "Damping", light.damping, light.damping_anim)
        fw("}\n")


def write_static_or_animated(fw: TextIO.write, global_seqs: Set[int], name: str, value: float, anim: War3AnimationCurve):
    if anim is not None:
        write_animated(fw, global_seqs, name, anim)
    else:
        fw("\tstatic %s %s,\n" % (name, float2str(value)))


def write_animated(fw: TextIO.write, global_seqs: Set[int], name: str, visibility: War3AnimationCurve):
    write_animation_chunk(fw, visibility, name, global_seqs, "\t")
    # write_animation_chunk(visibility.keyframes, visibility.type,
    #                       visibility.interpolation, visibility.global_sequence,
    #                       visibility.handles_left, visibility.handles_right,
    #                       name, fw, global_seqs, "\t")
