from typing import List

import bpy

from export_mdl import constants
from export_mdl.classes.War3Model import War3Model
from ..action_compat import find_fcurve, new_fcurve, own_fcurve
from ..geoset_preview import add_geoset_preview


def create_object_actions1(model: War3Model,
                           bpy_objects: List[bpy.types.Object],
                           frame_time: float):
    print("creating object animations")
    geoset_animations = model.geoset_anims
    sequences = model.sequences
    data_path_color = 'color'

    for geosetAnimation in geoset_animations:
        # geoset_id = geosetAnimation.geoset_id
        # action = bpy.data.actions.new(name='#UNANIMATED' + ' ' + bpy_objects[geoset_id].name)
        action = bpy.data.actions.new(name='#UNANIMATED' + ' ' + geosetAnimation.geoset_name)
        color_r = new_fcurve(action, data_path_color, 0)
        color_g = new_fcurve(action, data_path_color, 1)
        color_b = new_fcurve(action, data_path_color, 2)
        color_a = new_fcurve(action, data_path_color, 3)
        color_r.keyframe_points.insert(0.0, 1.0)
        color_g.keyframe_points.insert(0.0, 1.0)
        color_b.keyframe_points.insert(0.0, 1.0)
        color_a.keyframe_points.insert(0.0, 1.0)

    for sequence in sequences:
        interval_start = sequence.start
        interval_end = sequence.end
        for geosetAnimation in geoset_animations:
            # geoset_id = geosetAnimation.geoset_id
            color_anim = geosetAnimation.color_anim
            alpha_anim = geosetAnimation.alpha_anim
            # action = bpy.data.actions.new(name=sequence.name + ' ' + bpy_objects[geoset_id].name)
            action = bpy.data.actions.new(name=sequence.name + ' ' + geosetAnimation.geoset_name)
            color_r = None
            color_g = None
            color_b = None
            color_a = None
            interpolation_type = constants.INTERPOLATION_NAME_BLEND_NAME[color_anim.interpolation]

            for time, color in color_anim.keyframes.items():
                # time = color_anim.times[index]
                # color = color_anim.values[index]
                if interval_start <= time <= interval_end or time == 0:
                    if not color_r:
                        color_r = new_fcurve(action, data_path_color, 0)
                    if not color_g:
                        color_g = new_fcurve(action, data_path_color, 1)
                    if not color_b:
                        color_b = new_fcurve(action, data_path_color, 2)
                    if time == 0:
                        real_time = 0.0
                    else:
                        real_time = round((time - interval_start) / frame_time, 0)
                    color_r_keyframe = color_r.keyframe_points.insert(real_time, color[0])
                    color_g_keyframe = color_g.keyframe_points.insert(real_time, color[1])
                    color_b_keyframe = color_b.keyframe_points.insert(real_time, color[2])
                    color_r_keyframe.interpolation = interpolation_type
                    color_g_keyframe.interpolation = interpolation_type
                    color_b_keyframe.interpolation = interpolation_type
            if not color_r:
                color_r = new_fcurve(action, data_path_color, 0)
                color_r.keyframe_points.insert(0, 1.0)
            if not color_g:
                color_g = new_fcurve(action, data_path_color, 1)
                color_g.keyframe_points.insert(0, 1.0)
            if not color_b:
                color_b = new_fcurve(action, data_path_color, 2)
                color_b.keyframe_points.insert(0, 1.0)
            interpolation_type = constants.INTERPOLATION_NAME_BLEND_NAME[alpha_anim.interpolation]

            for time, alpha in color_anim.keyframes.items():
                # time = alpha_anim.times[index]
                # alpha = alpha_anim.values[index]
                if interval_start <= time <= interval_end or time == 0:
                    if not color_a:
                        color_a = new_fcurve(action, data_path_color, 3)
                    if time == 0:
                        real_time = 0.0
                    else:
                        real_time = round((time - interval_start) / frame_time, 0)
                    color_a_keyframe = color_a.keyframe_points.insert(real_time, alpha)
                    color_a_keyframe.interpolation = interpolation_type
            if not color_a:
                color_a = new_fcurve(action, data_path_color, 3)
                color_a.keyframe_points.insert(0, 1.0)


def create_geoset_actions(model: War3Model,
                          bpy_objects: List[bpy.types.Object],
                          frame_time: float):
    """Geoset animations go on each mesh object's Warcraft 3 Geoset Animation properties (Object tab), keyed on
    the scene timeline like the sequence markers. Global-sequence tracks become looping (Cycles) curves."""
    print(" creating geoset animations")
    durations = getattr(model, "global_sequence_durations", [])
    for geoset_anim in model.geoset_anims:
        if not 0 <= geoset_anim.geoset_id < len(bpy_objects):
            continue
        obj = bpy_objects[geoset_anim.geoset_id]
        props = obj.mdl_geoset
        if geoset_anim.alpha:
            props.alpha = geoset_anim.alpha[0]
        if geoset_anim.color is not None:
            # MDX stores colors RGB
            props.color = tuple(geoset_anim.color[:3])
        static_alpha = props.alpha
        static_color = tuple(props.color)
        key_track(obj, 'alpha', geoset_anim.alpha_anim, frame_time, durations, lambda v: v[0],
                  model.sequences, static_alpha)
        key_track(obj, 'color', geoset_anim.color_anim, frame_time, durations, lambda v: tuple(v[:3]),
                  model.sequences, static_color)
        add_geoset_preview(obj)


def key_track(obj: bpy.types.Object, prop: str, curve, frame_time: float, durations: List[int], convert,
              sequences, static):
    if curve is None or not curve.keyframes:
        return
    props = obj.mdl_geoset
    data_path = 'mdl_geoset.' + prop
    gs = curve.global_sequence
    looping = isinstance(gs, int) and 0 <= gs < len(durations)
    keys = {round(time / frame_time): convert(value) for time, value in curve.keyframes.items()}
    if not looping:
        # The game shows the static value in a sequence without keys, Blender would hold the previous key
        for sequence in sequences:
            if not any(sequence.start <= time <= sequence.end for time in curve.keyframes):
                keys.setdefault(round(sequence.start / frame_time), static)
    for frame, value in sorted(keys.items()):
        setattr(props, prop, value)
        obj.keyframe_insert(data_path=data_path, frame=frame, group="Geoset Animation")
    interpolation = constants.INTERPOLATION_NAME_BLEND_NAME.get(curve.interpolation, 'LINEAR')
    channels = 3 if prop == 'color' else 1
    for index in range(channels):
        fcurve = own_fcurve(obj, data_path, index)
        if fcurve is None:
            continue
        for point in fcurve.keyframe_points:
            point.interpolation = interpolation
        if looping:
            end = round(durations[gs] / frame_time)
            if fcurve.keyframe_points[-1].co[0] < end:
                # The loop length is where the curve ends, so close it with the first value
                fcurve.keyframe_points.insert(end, fcurve.keyframe_points[0].co[1]).interpolation = interpolation
            fcurve.modifiers.new('CYCLES')
