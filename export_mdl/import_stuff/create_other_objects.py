from typing import List, Dict, Optional

import bpy
from mathutils import Matrix, Vector, Quaternion

from export_mdl import constants
from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3Attachment import War3Attachment
from export_mdl.classes.War3Bone import War3Bone
from export_mdl.classes.War3CollisionShape import War3CollisionShape
from export_mdl.classes.War3EventObject import War3EventObject
from export_mdl.classes.War3Helper import War3Helper
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Node import War3Node
from export_mdl.import_stuff.create_attachment_empties import create_attachment_empties
from export_mdl.import_stuff.create_collision_empties import create_collision_empties
from export_mdl.import_stuff.create_event_empties import create_event_empties
from export_mdl.import_stuff.create_light_objects import create_light_objects


def create_other_objects(model: War3Model,
                         bpy_armature_object: bpy.types.Object,
                         bone_size: float,
                         fps_ratio: float):
    print(" creating other objects")

    bpy.ops.object.mode_set(mode='EDIT')

    collisions = create_collision_empties(model.collision_shapes, bpy_armature_object)
    animate_objects(fps_ratio, model.sequences, model.collision_shapes, collisions)

    attachments = create_attachment_empties(bone_size, model.attachments, bpy_armature_object)
    animate_objects(fps_ratio, model.sequences, model.attachments, attachments)

    events = create_event_empties(bone_size, model.event_objects, bpy_armature_object)
    animate_objects(fps_ratio, model.sequences, model.event_objects, events)

    lights = create_light_objects(model.lights, bpy_armature_object)
    animate_objects(fps_ratio, model.sequences, model.lights, lights)

    bpy.ops.object.mode_set(mode='OBJECT')


def animate_objects(fps_ratio, sequences: List[War3AnimationAction], nodes: List[War3Node], bpy_objects: List[bpy.types.Object]):
    rotation_adjust: Dict[str, Matrix] = {}
    # for bpy_object in bpy_objects:
    #     mat = Matrix(bpy_object.matrix_basis)
    #     mat.invert()
    #     rotation_adjust[bpy_object.name] = mat

    identity = Matrix().Identity(4)
    for sequence in sequences:
        action: bpy.types.Action = bpy.data.actions.get(sequence.name)

        for node in nodes:
            # print("adding action %s to: " % sequence.name, node.name)
            matrix: Matrix = rotation_adjust.get(node.name, identity)
            add_actions_to_node(action, fps_ratio, 0, sequence.end, sequence.start, node, matrix)
            # add_actions_to_node2(action, fps_ratio, 0, sequence, node, matrix)

    action_all: bpy.types.Action = bpy.data.actions.get("all sequences")
    for sequence in sequences:
        for node in nodes:
            matrix: Matrix = rotation_adjust.get(node.name, identity)
            add_actions_to_node(action_all, fps_ratio, sequence.start, sequence.end, sequence.start, node, matrix)
            # add_actions_to_node2(action_all, fps_ratio, sequence.start, sequence, node, matrix)


def add_actions_to_node(action: bpy.types.Action,
                        fps_ratio: float,
                        timeline_offset: float,
                        interval_end: float,
                        interval_start: float,
                        node: War3Node,
                        matrix: Matrix):
    bone_name = node.name
    translations: Optional[War3AnimationCurve] = node.anim_loc
    rotations: Optional[War3AnimationCurve] = node.anim_rot
    scalings: Optional[War3AnimationCurve] = node.anim_scale

    if translations:
        # print("translations!")
        create_transformation_curves(action, bone_name, 'location',
                                     fps_ratio, interval_end, interval_start, timeline_offset,
                                     translations, [0.0, 0.0, 0.0], matrix)
    if rotations:
        # print("rotations!")
        create_transformation_curves(action, bone_name, 'rotation_quaternion',
                                     fps_ratio, interval_end, interval_start,
                                     timeline_offset, rotations, [1.0, 0.0, 0.0, 0.0], matrix)

    if scalings:
        # print("scalings!")
        create_transformation_curves(action, bone_name, 'scale',
                                     fps_ratio, interval_end, interval_start, timeline_offset,
                                     scalings, [1.0, 1.0, 1.0], matrix)


def create_transformation_curves(action: bpy.types.Action,
                                 object_name: str,
                                 data_path_addition: str,
                                 fps_ratio: float,
                                 interval_end: float,
                                 interval_start: float,
                                 timeline_offset: float,
                                 transformations: War3AnimationCurve,
                                 trans_zero_values: List[float], matrix: Matrix):
    data_path = 'bpy.data.objects["' + object_name + '"].' + data_path_addition
    starting_keyframe = round(timeline_offset / fps_ratio, 0)
    interpolation_type = constants.INTERPOLATION_NAME_BLEND_NAME[transformations.interpolation]

    fcurves: List[bpy.types.FCurve] = []

    current_fcurve = action.fcurves.find(data_path)
    if current_fcurve is not None:
        current_fcurve_index = action.fcurves.values().index(current_fcurve)
        for i in range(len(trans_zero_values)):
            fcurves.append(action.fcurves[current_fcurve_index + i])

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
        set_new_curves(action, object_name, data_path, fcurves, starting_keyframe - 1, value, None, None, interpolation_type)
        set_new_curves(action, object_name, data_path, fcurves, end_keyframe + 1, value, None, None, interpolation_type)

        value: List[float] = list(transformations.keyframes.get(interval_start, trans_zero_values))
        if data_path_addition == 'rotation_quaternion':
            # if value[0] < 0:
            #     for i in range(len(value)):
            #         value[i] = value[i] * -1.0
            value = rotate_quat(matrix, value)
        if data_path_addition == 'location':
            value = rotate_vec3(matrix, value)
        set_new_curves(action, object_name, data_path, fcurves, end_keyframe, value, None, None, interpolation_type)



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
            set_new_curves(action, object_name, data_path, fcurves, real_time, value, h_left, h_right, interpolation_type)


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
            fcurves_new = action.fcurves.new(data_path, index=i, action_group=bone_name)
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


def get_bone_group_color(nodeType) -> str:
    if nodeType == 'bone':
        return 'THEME04'
    elif nodeType == 'attachment':
        return 'THEME09'
    elif nodeType == 'collision_shape':
        return 'THEME02'
    elif nodeType == 'event':
        return 'THEME03'
    elif nodeType == 'helper':
        return 'THEME01'
    return 'DEFAULT'


def get_node_type(node: War3Node) -> str:
    if isinstance(node, War3Bone):
        return 'bone'
    elif isinstance(node, War3Attachment):
        return 'attachment'
    elif isinstance(node, War3CollisionShape):
        return 'collision_shape'
    elif isinstance(node, War3EventObject):
        return 'event'
    elif isinstance(node, War3Helper):
        return 'helper'
    return 'default'
