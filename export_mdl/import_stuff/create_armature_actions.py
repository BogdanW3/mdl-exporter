from typing import Optional, List, Dict, Tuple

import bpy
from mathutils import Matrix, Vector, Quaternion

from export_mdl import constants, War3ArmatureProperties, War3ArmatureSequenceListItem
from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Node import War3Node
from ..action_compat import find_fcurve, new_fcurve
from .key_tracks import apply_tangents, game_value, shape_sequence_bounds, bake_curved_rotation


def create_armature_actions(armature_object: bpy.types.Object, model: War3Model, fps_ratio: float):
    print(" adding animations")
    nodes: List[War3Node] = list(getattr(model, "armature_nodes", None) or (list(model.bones) + list(model.helpers)))
    sequences: List[War3AnimationAction] = model.sequences
    armature: bpy.types.Armature = armature_object.data
    action_unanimated = bpy.data.actions.new(name='#UNANIMATED')
    war3_armature_properties: War3ArmatureProperties = armature.war_3
    war3_armature_properties.sequencesList.add().name = '#UNANIMATED'

    action_all = bpy.data.actions.new(name='all sequences')
    war3_armature_properties.sequencesList.add().name = 'all sequences'

    # Curved rotations become linear keys that follow the game's curve (see bake_curved_rotation)
    spans = [(sequence.start, sequence.end) for sequence in sequences]
    for node in nodes:
        node.anim_rot = bake_curved_rotation(node.anim_rot, spans, fps_ratio,
                                             getattr(model, "global_sequence_durations", []))

    for node in nodes:
        # print("adding unanimated to: ", node.name)
        add_unanimated_to_bones(action_unanimated, node, node.name)
        add_unanimated_to_bones(action_all, node, node.name)

    bpy.ops.object.mode_set(mode='EDIT')

    rotation_adjust: Dict[str, Matrix] = {}
    for bone in armature.edit_bones:
        mat = Matrix(bone.matrix)
        mat.invert()
        rotation_adjust[bone.name] = mat

    bpy.ops.object.mode_set(mode='OBJECT')
    create_bpy_actions(sequences, war3_armature_properties, fps_ratio)

    create_timeline_markers(fps_ratio, sequences)

    # Tracks on a global sequence loop on their own, independent of the sequences: they're set aside here and
    # become looping (Cycles) curves in "all sequences", starting at frame 0
    durations = getattr(model, "global_sequence_durations", [])
    looping: List = []
    for node in nodes:
        for attr in ('anim_loc', 'anim_rot', 'anim_scale'):
            curve = getattr(node, attr)
            gs = curve.global_sequence if curve is not None else None
            if isinstance(gs, int) and 0 <= gs < len(durations):
                looping.append((node, attr, curve, durations[gs]))
                setattr(node, attr, None)

    identity = Matrix().Identity(4)
    for sequence in sequences:
        action: bpy.types.Action = bpy.data.actions.get(sequence.name)

        for node in nodes:
            # print("adding action %s to: " % sequence.name, node.name)
            matrix: Matrix = rotation_adjust.get(node.name, identity)
            add_actions_to_node(action, fps_ratio, 0, sequence.end, sequence.start, node, matrix)
            # add_actions_to_node2(action, fps_ratio, 0, sequence, node, matrix)

    # Frames the sequences cover: the rest-pose padding around each sequence must not land on another one's keys
    # (two sequences can be a single frame apart)
    occupied = [(round(s.start / fps_ratio), round(s.end / fps_ratio)) for s in sequences]
    for sequence in sequences:
        for node in nodes:
            matrix: Matrix = rotation_adjust.get(node.name, identity)
            add_actions_to_node(action_all, fps_ratio, sequence.start, sequence.end, sequence.start, node, matrix,
                                occupied)
            # add_actions_to_node2(action_all, fps_ratio, sequence.start, sequence, node, matrix)

    paths = {'anim_loc': ('location', [0.0, 0.0, 0.0]), 'anim_rot': ('rotation_quaternion', [1.0, 0.0, 0.0, 0.0]),
             'anim_scale': ('scale', [1.0, 1.0, 1.0])}
    for node, attr, curve, duration in looping:
        setattr(node, attr, curve)
        path, zero = paths[attr]
        matrix = rotation_adjust.get(node.name, identity)
        data_path = 'pose.bones["' + node.name + '"].' + path
        # Replace whatever the rest pose put there with the looping track
        for index in range(len(zero)):
            fcurve = find_fcurve(action_all, data_path, index)
            if fcurve is not None:
                fcurve.keyframe_points.clear()
        create_transformation_curves(action_all, node.name, path, fps_ratio, duration, 0, 0, curve, zero, matrix)
        end = round(duration / fps_ratio)
        for index in range(len(zero)):
            fcurve = find_fcurve(action_all, data_path, index)
            if fcurve is None or not len(fcurve.keyframe_points):
                continue
            if fcurve.keyframe_points[-1].co[0] < end:
                first = fcurve.keyframe_points[0]
                fcurve.keyframe_points.insert(end, first.co[1]).interpolation = first.interpolation
            fcurve.modifiers.new('CYCLES')

    # Curved (Hermite/Bezier) translation and scaling keep their shape: handles from the file's tangents, in
    # "all sequences" (what the exporter reads). Rotations interpolate on the sphere, so they're left as they are.
    for node in nodes:
        matrix = rotation_adjust.get(node.name, identity)
        for attr, path, convert in (('anim_loc', 'location', lambda v, m=matrix: rotate_vec3(m, v)),
                                    ('anim_scale', 'scale', lambda v: v)):
            curve = getattr(node, attr)
            if curve is None:
                continue
            data_path = 'pose.bones["' + node.name + '"].' + path
            fcurves = [find_fcurve(action_all, data_path, index) for index in range(3)]
            apply_tangents(fcurves, curve, fps_ratio, convert)
            shape_sequence_bounds(fcurves, curve, fps_ratio, sequences, convert)


def add_unanimated_to_bones(action: bpy.types.Action, node: War3Node, bone_name: str):
    loc_interp = 'CONSTANT' if not node.anim_loc else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_loc.interpolation]
    rot_interp = 'CONSTANT' if not node.anim_rot else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_rot.interpolation]
    scale_interp = 'CONSTANT' if not node.anim_scale else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_scale.interpolation]

    data_path = 'pose.bones["' + bone_name + '"]'
    set_new_curves(action, bone_name, data_path + '.location', [], 0, [0.0, 0.0, 0.0], None, None, loc_interp)
    set_new_curves(action, bone_name, data_path + '.rotation_quaternion', [], 0, [1.0, 0.0, 0.0, 0.0], None, None, rot_interp)
    set_new_curves(action, bone_name, data_path + '.scale', [], 0, [1.0, 1.0, 1.0], None, None, scale_interp)


def create_timeline_markers(frame_time: float, sequences: List[War3AnimationAction]):
    scene = bpy.data.scenes[0]
    for sequence in sequences:
        int_start: int = round(sequence.start / frame_time, None)
        int_end: int = round(sequence.end / frame_time, None)

        scene.timeline_markers.new(sequence.name, frame=int_start)
        scene.timeline_markers.new(sequence.name, frame=int_end)

    # The scene's sequence list (what the exporter writes), in the file's order and with its settings. Without
    # this the list is filled from the markers later, with guessed settings.
    window_manager = bpy.context.window_manager
    refreshing = window_manager.mdl_sequence_refreshing
    window_manager.mdl_sequence_refreshing = True  # Keep the marker sync handler out while we fill it
    try:
        scene_sequences = scene.war3_mdl_sequences.mdl_sequences
        for index, sequence in enumerate(sequences):
            found = scene_sequences.find(sequence.name)
            item = scene_sequences[found] if found >= 0 else scene_sequences.add()
            item.seq_name = sequence.name
            item.name = sequence.name
            item.non_looping = bool(sequence.non_looping)
            item.rarity = int(round(sequence.rarity))
            item.move_speed = int(round(sequence.movement_speed))
            scene_sequences.move(scene_sequences.find(sequence.name), index)
    finally:
        window_manager.mdl_sequence_refreshing = refreshing


def create_bpy_actions(sequences: List[War3AnimationAction],
                       war3_armature_properties: War3ArmatureProperties,
                       fps_ratio: float):
    for sequence in sequences:
        war3_Sequence: War3ArmatureSequenceListItem = war3_armature_properties.sequencesList.add()
        war3_Sequence.name = sequence.name
        war3_Sequence.length = int(round((sequence.end - sequence.start)/fps_ratio, 0))
        if not bpy.data.actions.get(sequence.name):
            bpy_action = bpy.data.actions.new(name=war3_Sequence.name)
            war3_Sequence.action_name = bpy_action.name


def add_actions_to_node(action: bpy.types.Action,
                        fps_ratio: float,
                        timeline_offset: float,
                        interval_end: float,
                        interval_start: float,
                        node: War3Node,
                        matrix: Matrix,
                        occupied=()):
    bone_name = node.name
    translations: Optional[War3AnimationCurve] = node.anim_loc
    rotations: Optional[War3AnimationCurve] = node.anim_rot
    scalings: Optional[War3AnimationCurve] = node.anim_scale

    if translations:
        # print("translations!")
        create_transformation_curves(action, bone_name, 'location',
                                     fps_ratio, interval_end, interval_start, timeline_offset,
                                     translations, [0.0, 0.0, 0.0], matrix, occupied)
    if rotations:
        # print("rotations!")
        create_transformation_curves(action, bone_name, 'rotation_quaternion',
                                     fps_ratio, interval_end, interval_start,
                                     timeline_offset, rotations, [1.0, 0.0, 0.0, 0.0], matrix, occupied)

    if scalings:
        # print("scalings!")
        create_transformation_curves(action, bone_name, 'scale',
                                     fps_ratio, interval_end, interval_start, timeline_offset,
                                     scalings, [1.0, 1.0, 1.0], matrix, occupied)


def add_actions_to_node2(action: bpy.types.Action,
                         fps_ratio: float,
                         timeline_offset: float,
                         sequence: War3AnimationAction,
                         node: War3Node,
                         matrix: Matrix):
    bone_name = node.name
    data_path = 'pose.bones["' + bone_name + '"].'
    translations: Optional[War3AnimationCurve] = node.anim_loc
    rotations: Optional[War3AnimationCurve] = node.anim_rot
    scalings: Optional[War3AnimationCurve] = node.anim_scale

    trans_dict = get_sequence_dict(sequence, node.anim_loc, lambda v: rotate_vec3(matrix, v))
    trans_interp = 'CONSTANT' if node.anim_loc is None else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_loc.interpolation]
    set_new_curve1(action, bone_name, data_path + 'location', trans_dict, [0.0, 0.0, 0.0], fps_ratio, sequence.start - timeline_offset, trans_interp)

    rot_dict = get_sequence_dict(sequence, node.anim_rot, lambda v: rotate_quat(matrix, v))
    rot_interp = 'CONSTANT' if node.anim_rot is None else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_rot.interpolation]
    set_new_curve1(action, bone_name, data_path + 'rotation_quaternion', rot_dict, [1.0, 0.0, 0.0, 0.0], fps_ratio, sequence.start - timeline_offset, rot_interp)

    scale_dict = get_sequence_dict(sequence, node.anim_scale, lambda v: v)
    scale_interp = 'CONSTANT' if node.anim_scale is None else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_scale.interpolation]
    set_new_curve1(action, bone_name, data_path + 'scale', scale_dict, [1.0, 1.0, 1.0], fps_ratio, sequence.start - timeline_offset, scale_interp)


def create_transformation_curves(action: bpy.types.Action,
                                 bone_name: str,
                                 data_path_addition: str,
                                 fps_ratio: float,
                                 interval_end: float,
                                 interval_start: float,
                                 timeline_offset: float,
                                 transformations: War3AnimationCurve,
                                 trans_zero_values: List[float], matrix: Matrix, occupied=()):
    data_path = 'pose.bones["' + bone_name + '"].' + data_path_addition
    starting_keyframe = round(timeline_offset / fps_ratio, 0)
    interpolation_type = constants.INTERPOLATION_NAME_BLEND_NAME[transformations.interpolation]

    fcurves: List[bpy.types.FCurve] = []

    if find_fcurve(action, data_path) is not None:
        for i in range(len(trans_zero_values)):
            fcurves.append(find_fcurve(action, data_path, i))

    # set the keyframe before and after the sequence to same as the first keyframe,
    # or T-pose if first keyframe is not present, to not ge weird
    # transitions between actions in "all sequences" in the case transformation is not set
    h_lefts = transformations.handles_left
    h_rights = transformations.handles_right
    if timeline_offset != 0:
        # value: List[float] = list(transformations.keyframes.get(interval_start, trans_zero_values))
        value: List[float] = list(trans_zero_values)

        if data_path_addition == 'rotation_quaternion':
            # if value[0] < 0:
            #     for i in range(len(value)):
            #         value[i] = value[i] * -1.0
            value = rotate_quat(matrix, value)
        if data_path_addition == 'location':
            value = rotate_vec3(matrix, value)

        end_keyframe = round((interval_end + timeline_offset - interval_start) / fps_ratio, 0)
        for frame in (starting_keyframe - 1, end_keyframe + 1):
            if not any(start <= frame <= end for start, end in occupied):
                set_new_curves(action, bone_name, data_path, fcurves, frame, value, None, None, interpolation_type)

        # Keys at the start and end with what the game shows there: past the last key it blends back toward the
        # first, before the first one it extrapolates. Blender then plays the same, and the end of one sequence
        # doesn't run into the next. (Real keys at those frames replace them below.)
        quaternion = data_path_addition == 'rotation_quaternion'
        in_sequence = [t for t in transformations.keyframes if interval_start <= t <= interval_end]
        bounds = [(end_keyframe, interval_end)]
        if in_sequence and min(in_sequence) > interval_start:
            bounds.append((starting_keyframe, interval_start))
        for frame, time in bounds:
            value = game_value(transformations, time, interval_start, interval_end, quaternion)
            value = list(trans_zero_values) if value is None else value
            if quaternion:
                value = rotate_quat(matrix, value)
            if data_path_addition == 'location':
                value = rotate_vec3(matrix, value)
            set_new_curves(action, bone_name, data_path, fcurves, frame, value, None, None, interpolation_type)



    for time, transformation in transformations.keyframes.items():

        if interval_start <= time <= interval_end:
            real_time = round((time + timeline_offset - interval_start) / fps_ratio, 0)
            value = list(transformation)
            # h_left = list(h_lefts.get(time))
            # h_right = list(h_rights.get(time))
            h_left: Optional[List[float]] = None
            h_right: Optional[List[float]] = None
            # if data_path_addition == 'rotation_quaternion' and value[0] < 0:
            #     for i in range(len(value)):
            #         value[i] = value[i] * -1.0

            if data_path_addition == 'rotation_quaternion':
                # if value[0] < 0:
                #     for i in range(len(value)):
                #         value[i] = value[i] * -1.0
                value = rotate_quat(matrix, value)
                if time in h_lefts and h_lefts.get(time):
                    h_left = rotate_quat(matrix, list(h_lefts.get(time)))
                if time in h_rights and h_rights.get(time):
                    h_right = rotate_quat(matrix, list(h_rights.get(time)))
            if data_path_addition == 'location':
                value = rotate_vec3(matrix, value)
                if h_left:
                    h_left = rotate_vec3(matrix, h_left)
                if h_right:
                    h_right = rotate_vec3(matrix, h_right)
            set_new_curves(action, bone_name, data_path, fcurves, real_time, value, h_left, h_right, interpolation_type)


def rotate_vec3(matrix: Matrix, value: List[float]):
    vec = Vector(value)
    vec.rotate(matrix)
    value = list(vec)
    return value


def rotate_quat(matrix: Matrix, value: List[float]):
    # if value[0] < 0:
    #     for i in range(len(value)):
    #         value[i] = value[i] * -1.0
    axis, angle = Quaternion(value).to_axis_angle()
    axis.rotate(matrix)
    quat = Quaternion(Vector(axis), angle)
    quat.normalize()
    value = list(quat)
    if value[0] < 0:
        for i in range(len(value)):
            value[i] = value[i] * -1.0
    return value


def set_new_curves(action: bpy.types.Action,
                   bone_name: str,
                   data_path: str,
                   fcurves: List[bpy.types.FCurve],
                   keyframe: float,
                   value: Optional[List[float]],
                   h_left: Optional[List[float]],
                   h_right: Optional[List[float]],
                   interpolation: str = 'CONSTANT'):
    # print("fcurves: ", fcurves)
    # if h_left and h_right and 'rotation' in data_path:
    #     quat = Quaternion(value)
    #     quat2 = Quaternion(h_left)
    #     quat.rotate(quat2)
    #     h_left = list(quat)
    #     quat = Quaternion(value)
    #     quat2 = Quaternion(h_right)
    #     quat.rotate(quat2)
    #     h_right = list(quat)


    for i in range(len(value)):
        if len(fcurves) <= i:
            fcurves_new = new_fcurve(action, data_path, i, bone_name)
            fcurves.append(fcurves_new)
        org_len = len(fcurves[i].keyframe_points)
        if value is not None and i < len(value):
            kf_point = fcurves[i].keyframe_points.insert(keyframe, value[i])
            kf_point.interpolation = interpolation
            # if h_left and h_right:
            #     # kf_point.handle_left_type = 'FREE'
            #     # kf_point.handle_right_type = 'FREE'
            #     # kf_point.handle_left = (keyframe-1, value[i] + h_left[i])
            #     if 'rotation' not in data_path:
            #         kf_point.handle_left = (kf_point.handle_left[0], kf_point.handle_left[1] + h_left[i])
            #         kf_point.handle_right = (kf_point.handle_right[0], kf_point.handle_right[1] + h_right[i])
            #     else:
            #         kf_point.handle_left_type = 'FREE'
            #         kf_point.handle_right_type = 'FREE'
            #         kf_point.handle_left = (kf_point.handle_left[0], h_left[i])
            #         kf_point.handle_right = (kf_point.handle_right[0], h_right[i])
            # # if h_right:
            # #     # kf_point.handle_right_type = 'FREE'
            # #     # kf_point.handle_right = (keyframe+1, value[i] + h_right[i])
    return fcurves


def set_new_curve1(action: bpy.types.Action,
                   bone_name: str,
                   data_path: str,
                   sequence_dict: Dict[float, Tuple[List[float], Optional[List[float]], Optional[List[float]]]],
                   trans_zero_values: List[float],
                   fps_ratio: float,
                   timeline_offset: float,
                   interpolation: str = 'CONSTANT'):
    # print("fcurves: ", fcurves)

    fcurves: List[bpy.types.FCurve] = []

    if find_fcurve(action, data_path) is not None:
        for i in range(len(trans_zero_values)):
            fcurves.append(find_fcurve(action, data_path, i))

    if len(sequence_dict):
        first_time = list(sequence_dict)[0]
        first_value = sequence_dict[first_time][0]
        for i in range(len(first_value)):
            if len(fcurves) <= i:
                fcurves_new = new_fcurve(action, data_path, i, bone_name)
                fcurves.append(fcurves_new)

    # for time, value, h_left, h_right in sequence_dict.items():
    for time, kf in sequence_dict.items():
        value, h_left, h_right = kf
        keyframe = round((time - timeline_offset)/fps_ratio, 0)
        for i in range(len(value)):
            if i < len(value):
                kf_point = fcurves[i].keyframe_points.insert(keyframe, value[i])
                kf_point.interpolation = interpolation
                # kf_point.co_ui = (keyframe, value[i])
                if h_left and h_right:
                    kf_point.handle_left_type = 'FREE'
                    kf_point.handle_right_type = 'FREE'
                    # kf_point.handle_left = (keyframe-1, value[i] + h_left[i])
                    # kf_point.handle_right = (keyframe+1, value[i] + h_right[i])
                    # kf_point.handle_left = (kf_point.handle_left[0], kf_point.handle_left[1] + h_left[i])
                    # kf_point.handle_right = (kf_point.handle_right[0], kf_point.handle_right[1] + h_right[i])
                    if 'rotation' not in data_path:
                        kf_point.handle_left = (kf_point.handle_left[0], h_left[i])
                        kf_point.handle_right = (kf_point.handle_right[0], h_right[i])
                    else:
                        kf_point.handle_left = (kf_point.handle_left[0], h_left[i])
                        kf_point.handle_right = (kf_point.handle_right[0], h_right[i])

    # if len(sequence_dict):
    #     first_time = list(sequence_dict)[0]
    #     first_value = sequence_dict[first_time][0]
    #     for i in range(len(first_value)):
    #         for kf_point in fcurves[i].keyframe_points[org_leng[i]:]:
    #             kf_point.handle_left_type = 'FREE'
    #             kf_point.handle_right_type = 'FREE'
    #
    # for kf_i, time in enumerate(sequence_dict):
    #     value, h_left, h_right = sequence_dict[time]
    #     # keyframe = (time - timeline_offset)/fps_ratio
    #     for i in range(len(value)):
    #         if i < len(value) and h_left and h_right:
    #             kf_point = fcurves[i].keyframe_points[kf_i + org_leng[i]]
    #             # kf_point.handle_left_type = 'FREE'
    #             # kf_point.handle_right_type = 'FREE'
    #             # kf_point.handle_left = (keyframe-1, value[i] + h_left[i])
    #             # kf_point.handle_right = (keyframe+1, value[i] + h_right[i])
    #             kf_point.handle_left = (kf_point.handle_left[0], kf_point.handle_left[1] + h_left[i])
    #             kf_point.handle_right = (kf_point.handle_right[0], kf_point.handle_right[1] + h_right[i])

    return fcurves


# def set_new_curve1(action: bpy.types.Action,
#                    bone_name: str,
#                    data_path: str,
#                    sequence_dict: Dict[float, Tuple[List[float], Optional[List[float]], Optional[List[float]]]],
#                    trans_zero_values: List[float],
#                    fps_ratio: float,
#                    timeline_offset: float,
#                    interpolation: str = 'CONSTANT'):
#     # print("fcurves: ", fcurves)
#
#     fcurves: List[bpy.types.FCurve] = []
#
#     current_fcurve = action.fcurves.find(data_path)
#     if current_fcurve is not None:
#         current_fcurve_index = action.fcurves.values().index(current_fcurve)
#         for i in range(len(trans_zero_values)):
#             fcurves.append(action.fcurves[current_fcurve_index + i])
#
#     org_leng: Dict[int, int] = {}
#     if len(sequence_dict):
#         first_time = list(sequence_dict)[0]
#         first_value = sequence_dict[first_time][0]
#         for i in range(len(first_value)):
#             if len(fcurves) <= i:
#                 fcurves_new = new_fcurve(action, data_path, i, bone_name)
#                 fcurves.append(fcurves_new)
#             org_leng[i] = len(fcurves[i].keyframe_points)
#             fcurves[i].keyframe_points.add(len(sequence_dict))
#             # for kf_point in fcurves[i].keyframe_points[org_leng[i]:]:
#             #     kf_point.interpolation = interpolation
#             #     # if interpolation == 'BEZIER':
#             #     #     kf_point.handle_left_type = 'FREE'
#             #     #     kf_point.handle_right_type = 'FREE'
#
#     for kf_i, time in enumerate(sequence_dict):
#         value, h_left, h_right = sequence_dict[time]
#         keyframe = (time - timeline_offset)/fps_ratio
#         for i in range(len(value)):
#             if i < len(value):
#                 # kf_point = fcurves[i].keyframe_points.insert(keyframe, value[i])
#                 kf_point = fcurves[i].keyframe_points[kf_i + org_leng[i]]
#                 kf_point.interpolation = interpolation
#                 kf_point.co_ui = (keyframe, value[i])
#                 # if h_left and h_right:
#                 #     kf_point.handle_left_type = 'FREE'
#                 #     kf_point.handle_right_type = 'FREE'
#                 #     # kf_point.handle_left = (keyframe-1, value[i] + h_left[i])
#                 #     # kf_point.handle_right = (keyframe+1, value[i] + h_right[i])
#                 #     kf_point.handle_left = (kf_point.handle_left[0], kf_point.handle_left[1] + h_left[i])
#                 #     kf_point.handle_right = (kf_point.handle_right[0], kf_point.handle_right[1] + h_right[i])
#
#     # if len(sequence_dict):
#     #     first_time = list(sequence_dict)[0]
#     #     first_value = sequence_dict[first_time][0]
#     #     for i in range(len(first_value)):
#     #         for kf_point in fcurves[i].keyframe_points[org_leng[i]:]:
#     #             kf_point.handle_left_type = 'FREE'
#     #             kf_point.handle_right_type = 'FREE'
#     #
#     # for kf_i, time in enumerate(sequence_dict):
#     #     value, h_left, h_right = sequence_dict[time]
#     #     # keyframe = (time - timeline_offset)/fps_ratio
#     #     for i in range(len(value)):
#     #         if i < len(value) and h_left and h_right:
#     #             kf_point = fcurves[i].keyframe_points[kf_i + org_leng[i]]
#     #             # kf_point.handle_left_type = 'FREE'
#     #             # kf_point.handle_right_type = 'FREE'
#     #             # kf_point.handle_left = (keyframe-1, value[i] + h_left[i])
#     #             # kf_point.handle_right = (keyframe+1, value[i] + h_right[i])
#     #             kf_point.handle_left = (kf_point.handle_left[0], kf_point.handle_left[1] + h_left[i])
#     #             kf_point.handle_right = (kf_point.handle_right[0], kf_point.handle_right[1] + h_right[i])
#
#     return fcurves


def get_sequence_dict(sequence: War3AnimationAction,
                      transformations: War3AnimationCurve, value_transform)\
        -> Dict[float, Tuple[List[float], Optional[List[float]], Optional[List[float]]]]:
    sequence_dict: Dict[float, Tuple[List[float], Optional[List[float]], Optional[List[float]]]] = {}
    if transformations:
        all_times = sorted(transformations.keyframes)
        start_int = 0
        if sequence.start not in all_times:
            all_times.append(sequence.start)
            all_times.sort()
            start_int = all_times.index(sequence.start)
            all_times.remove(sequence.start)
        else:
            start_int = all_times.index(sequence.start)
        end_ind = 0
        if sequence.end not in all_times:
            all_times.append(sequence.end)
            all_times.sort()
            end_ind = all_times.index(sequence.end)
            all_times.remove(sequence.end)
        else:
            end_ind = all_times.index(sequence.end)+1

        sequence_times = all_times[start_int:end_ind]
        sequence_dict = {}
        for time in sequence_times:
            value: List[float] = value_transform(transformations.keyframes.get(time))
            h_left: Optional[List[float]] = transformations.handles_left.get(time)
            h_right: Optional[List[float]] = transformations.handles_right.get(time)
            if h_left and h_right:
                h_left = value_transform(h_left)
                h_right = value_transform(h_right)
                # print(transformations.type)
                if transformations.type == 'Translation':
                    # print("Translation !!!! ", value, h_left, h_right)
                    print("Translation !!!!   ", [round(v, 6) for v in value], [round(v, 6) for v in h_left], [round(v, 6) for v in h_right])
                    # h_left = h_left + value
                    # h_right = h_right + value
                    h_left = [sum(x) for x in zip(h_left, value)]
                    h_right = [sum(x) for x in zip(h_right, value)]
                    print("->Translation !!!!_", [round(v, 6) for v in value], [round(v, 6) for v in h_left], [round(v, 6) for v in h_right])
                #     h_left = value_transform(h_left + transformations.keyframes.get(time))
                #     h_right = value_transform(h_right + transformations.keyframes.get(time))
                # else:
                #     h_left = value_transform(h_left)
                #     h_right = value_transform(h_right)


            sequence_dict[time] = (value, h_left, h_right)
            # print("entry for " + str(time), sequence_dict[time])
    return sequence_dict
