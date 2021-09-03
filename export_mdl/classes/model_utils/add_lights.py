from mathutils import Vector

from ..War3Model import War3Model
from ..War3Object import War3Object
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence


def add_lights(war3_model: War3Model, billboard_lock, billboarded, bpy_obj, settings):
    visibility = get_visibility(war3_model.sequences, bpy_obj)
    light = War3Object(bpy_obj.name)
    light.object = bpy_obj
    light.pivot = settings.global_matrix @ Vector(bpy_obj.location)
    light.billboarded = billboarded
    light.billboard_lock = billboard_lock

    if hasattr(bpy_obj.data, "mdl_light"):
        light_data = bpy_obj.data.mdl_light
        light.type = light_data.light_type

        light.intensity = light_data.intensity
        light.intensity_anim = get_wc3_animation_curve(bpy_obj.data.animation_data, 'mdl_light.intensity', 1, war3_model.sequences)
        # get_curve(obj.data, ['mdl_light.intensity'])

        register_global_sequence(war3_model.global_seqs, light.intensity_anim)

        light.atten_start = light_data.atten_start
        light.atten_start_anim = get_wc3_animation_curve(bpy_obj.data.animation_data, 'mdl_light.atten_start', 1, war3_model.sequences)
        # get_curve(obj.data, ['mdl_light.atten_start'])

        register_global_sequence(war3_model.global_seqs, light.atten_start_anim)

        light.atten_end = light_data.atten_end
        light.atten_end_anim = get_wc3_animation_curve(bpy_obj.data.animation_data, 'mdl_light.atten_end', 1, war3_model.sequences)
        # get_curve(obj.data, ['mdl_light.atten_end'])

        register_global_sequence(war3_model.global_seqs, light.atten_end_anim)

        light.color = light_data.color
        light.color_anim = get_wc3_animation_curve(bpy_obj.data.animation_data, 'mdl_light.color', 3, war3_model.sequences)
        # get_curve(obj.data, ['mdl_light.color'])

        register_global_sequence(war3_model.global_seqs, light.color_anim)

        light.amb_color = light_data.amb_color
        light.amb_color_anim = get_wc3_animation_curve(bpy_obj.data.animation_data, 'mdl_light.amb_color', 3, war3_model.sequences)
        # get_curve(obj.data, ['mdl_light.amb_color'])

        register_global_sequence(war3_model.global_seqs, light.amb_color_anim)

        light.amb_intensity = light_data.amb_intensity
        light.amb_intensity_anim = get_wc3_animation_curve(bpy_obj.data.animation_data, 'mdl_light.amb_intensity', 1, war3_model.sequences)
        # get_curve(obj.data, ['obj.mdl_light.amb_intensity'])

        register_global_sequence(war3_model.global_seqs, light.amb_intensity_anim)

    light.visibility = visibility
    register_global_sequence(war3_model.global_seqs, visibility)
    war3_model.objects['light'].add(light)
