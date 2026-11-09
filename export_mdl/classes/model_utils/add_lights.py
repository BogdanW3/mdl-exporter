from typing import Tuple, List, Set, Optional

import bpy
from mathutils import Vector, Matrix

from ..War3AnimationAction import War3AnimationAction
from ..War3Light import War3Light
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import get_visibility
from .object_node_transform import node_pivot, node_transform_curves, node_visibility
from ..animation_curve_utils.get_wc3_animation_curve import get_own_animation_curve
from ..bpy_helpers.BpyLight import BpyLight
from ...properties import War3LightSettings


def get_lights(sequences: List[War3AnimationAction],
               global_seqs: Set[int],
               actions: List[bpy.types.Action],
               bpy_light: BpyLight,
               global_matrix: Matrix) -> War3Light:
    bpy_obj = bpy_light.bpy_obj
    pivot = node_pivot(bpy_obj, global_matrix)
    anim_loc, anim_rot, anim_scale = node_transform_curves(bpy_obj, global_matrix, global_seqs, sequences)
    light = War3Light(bpy_light.name, -1, pivot, None, bpy_light.parent_name, anim_loc, anim_rot, anim_scale,
                      bpy_obj.matrix_basis)
    light.visibility = node_visibility(bpy_obj, global_seqs, sequences) \
        or get_visibility(sequences, global_seqs, actions, bpy_obj)

    light.billboarded = bpy_light.billboarded
    light.billboard_lock = bpy_light.billboard_lock
    light.node_flags = getattr(bpy_light, "node_flags", 0)

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
        light.light_type = light_data.light_type

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

        light.shadow_intensity = light_data.shadow_intensity
        light.shadow_casting = light_data.shadow_casting
        light.shadow_casting_start = light_data.shadow_casting_start
        light.shadow_casting_start_anim = anim_stuff(animation_data, actions, 'mdl_light.shadow_casting_start', 1, sequences, global_seqs)
        light.shadow_casting_end = light_data.shadow_casting_end
        light.shadow_casting_end_anim = anim_stuff(animation_data, actions, 'mdl_light.shadow_casting_end', 1, sequences, global_seqs)
        light.quadratic_falloff = light_data.quadratic_falloff
        light.quadratic_falloff_anim = anim_stuff(animation_data, actions, 'mdl_light.quadratic_falloff', 1, sequences, global_seqs)
        light.linear_falloff = light_data.linear_falloff
        light.linear_falloff_anim = anim_stuff(animation_data, actions, 'mdl_light.linear_falloff', 1, sequences, global_seqs)
        light.damping = light_data.damping
        light.damping_anim = anim_stuff(animation_data, actions, 'mdl_light.damping', 1, sequences, global_seqs)

    return light


def anim_stuff(animation_data: Optional[bpy.types.AnimData],
               actions: List[bpy.types.Action],
               data_path: str,
               num_indices: int,
               sequences: List[War3AnimationAction],
               global_seqs: Set[int]) -> Optional[War3AnimationCurve]:
    # Keys on the light datablock's own action first, then the older shared-action lookup
    id_data = animation_data.id_data if animation_data is not None else None
    curve = get_own_animation_curve(id_data, data_path, num_indices, global_seqs) if id_data is not None else None
    if curve is None:
        curve = get_wc3_animation_curve(data_path, actions, num_indices, sequences, global_seqs)
    return curve
