from typing import Tuple, List, Set, Optional

import bpy
from mathutils import Vector, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3ExportSettings import War3ExportSettings
from ..War3Light import War3Light
from ..War3Model import War3Model
from ..War3Node import War3Node
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import get_visibility
from ..bpy_helpers.BpyLight import BpyLight
from ...properties import War3LightSettings


def get_lights(sequences: List[War3AnimationAction],
               global_seqs: Set[int],
               actions: List[bpy.types.Action],
               bpy_light: BpyLight,
               global_matrix: Matrix):
    visibility = get_visibility(sequences, global_seqs, actions, bpy_light.bpy_obj)

    pivot = global_matrix @ Vector(bpy_light.location)
    light = War3Light(bpy_light.name, pivot, bpy_light.bpy_obj.matrix_basis)
    light.visibility = visibility

    light.billboarded = bpy_light.billboarded
    light.billboard_lock = bpy_light.billboard_lock

    # obj: bpy.types.Light = bpy_obj
    # bpy_light: bpy.types.Light = bpy_obj.data
    if isinstance(bpy_light.bpy_light, bpy.types.Light):
        print("data is Light")
    if isinstance(bpy_light.bpy_light, bpy.types.PointLight):
        print("data is PointLight")
    print("light data: ", bpy_light.bpy_light)

    animation_data = bpy_light.bpy_light.animation_data
    if hasattr(bpy_light.bpy_light, "mdl_light"):
        light_data: War3LightSettings = bpy_light.bpy_light.mdl_light
        light.type = light_data.light_type

        light.intensity = light_data.intensity
        light.intensity_anim = anim_stuff(animation_data, actions, 'mdl_light.intensity', 1, sequences, global_seqs)

        light.atten_start = light_data.atten_start
        light.atten_start_anim = anim_stuff(animation_data, actions, 'mdl_light.atten_start', 1, sequences, global_seqs)

        light.atten_end = light_data.atten_end
        light.atten_end_anim = anim_stuff(animation_data, actions, 'mdl_light.atten_end', 1, sequences, global_seqs)

        light.color = light_data.color
        light.color_anim = anim_stuff(animation_data, actions, 'mdl_light.color', 3, sequences, global_seqs)

        light.amb_color = light_data.amb_color
        light.amb_color_anim = anim_stuff(animation_data, actions, 'mdl_light.amb_color', 3, sequences, global_seqs)

        light.amb_intensity = light_data.amb_intensity
        light.amb_intensity_anim = anim_stuff(animation_data, actions, 'mdl_light.amb_intensity', 1, sequences, global_seqs)

    return light


def anim_stuff(animation_data: Optional[bpy.types.AnimData],
               actions: List[bpy.types.Action],
               data_path: str,
               num_indices: int,
               sequences: List[War3AnimationAction],
               global_seqs: Set[int]):
    curve = get_wc3_animation_curve(data_path, actions, num_indices, sequences, global_seqs)
    return curve
