from typing import Optional, List, Dict

import bpy
from mathutils import Matrix, Vector, Quaternion

from export_mdl import constants, War3ArmatureProperties
from export_mdl.classes.War3AnimationAction import War3AnimationAction
from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3Model import War3Model
from export_mdl.classes.War3Node import War3Node


def create_armature_actions(armature_object: bpy.types.Object, model: War3Model, frame_time: float):
    print("adding animations")
    nodes: List[War3Node] = model.objects_all
    sequences: List[War3AnimationAction] = model.sequences
    armature: bpy.types.Armature = armature_object.data
    action = bpy.data.actions.new(name='#UNANIMATED')
    war3_armature_properties: War3ArmatureProperties = armature.war_3
    war3_armature_properties.sequencesList.add().name = '#UNANIMATED'

    action_all = bpy.data.actions.new(name='all sequences')
    war3_armature_properties.sequencesList.add().name = 'all sequences'

    for node in nodes:
        add_unanimated_to_bones(action, node, node.name)
        add_unanimated_to_bones(action_all, node, node.name)

    bpy.ops.object.mode_set(mode='EDIT')

    rotation_adjust: Dict[str, Matrix] = {}
    for bone in armature.edit_bones:
        mat = Matrix(bone.matrix)
        mat.invert()
        rotation_adjust[bone.name] = mat

    bpy.ops.object.mode_set(mode='OBJECT')
    create_bpy_actions(sequences, war3_armature_properties)

    create_timeline_markers(frame_time, sequences)

    identity = Matrix().Identity(4)
    for sequence in sequences:
        action: bpy.types.Action = bpy.data.actions.get(sequence.name)

        for node in nodes:
            matrix: Matrix = rotation_adjust.get(node.name, identity)
            add_actions_to_node(action, frame_time, 0, sequence.end, sequence.start, node, matrix)

    for sequence in sequences:
        for node in nodes:
            matrix: Matrix = rotation_adjust.get(node.name, identity)
            add_actions_to_node(action_all, frame_time, sequence.start, sequence.end, sequence.start, node, matrix)


def create_timeline_markers(frame_time: float, sequences: List[War3AnimationAction]):
    for sequence in sequences:
        int_start: int = round(sequence.start / frame_time, None)
        int_end: int = round(sequence.end / frame_time, None)

        bpy.data.scenes[0].timeline_markers.new(sequence.name, frame=int_start)
        bpy.data.scenes[0].timeline_markers.new(sequence.name, frame=int_end)


def create_bpy_actions(sequences: List[War3AnimationAction], war3_armature_properties: War3ArmatureProperties):
    for sequence in sequences:
        print("adding sequence " + sequence.name)
        bpy.data.actions.new(name=sequence.name)
        war3_armature_properties.sequencesList.add().name = sequence.name


def add_actions_to_node(action: bpy.types.Action,
                        frame_time: float,
                        sequence_start: float,
                        interval_end: float,
                        interval_start: float,
                        node: War3Node,
                        matrix: Matrix):
    bone_name = node.name
    translations: Optional[War3AnimationCurve] = node.anim_loc
    rotations: Optional[War3AnimationCurve] = node.anim_rot
    scalings: Optional[War3AnimationCurve] = node.anim_scale

    if translations:
        create_transformation_curves(action, bone_name, 'location',
                                     frame_time, interval_end, interval_start, sequence_start,
                                     translations, [0.0, 0.0, 0.0], matrix)
    if rotations:
        create_transformation_curves(action, bone_name, 'rotation_quaternion',
                                     frame_time, interval_end, interval_start,
                                     sequence_start, rotations, [1.0, 0.0, 0.0, 0.0], matrix)

    if scalings:
        create_transformation_curves(action, bone_name, 'scale',
                                     frame_time, interval_end, interval_start, sequence_start,
                                     scalings, [1.0, 1.0, 1.0], matrix)


def create_transformation_curves(action: bpy.types.Action,
                                 bone_name: str,
                                 data_path_addition: str,
                                 frame_time: float,
                                 interval_end: float,
                                 interval_start: float,
                                 sequence_start: float,
                                 transformations: War3AnimationCurve,
                                 trans_zero_values: List[float], matrix: Matrix):
    data_path = 'pose.bones["' + bone_name + '"].' + data_path_addition
    starting_keyframe = round(sequence_start / frame_time, 0)
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
    value: List[float] = list(transformations.keyframes.get(interval_start, trans_zero_values))

    if data_path_addition == 'rotation_quaternion':
        if value[0] < 0:
            for i in range(len(value)):
                value[i] = value[i] * -1.0
        value = rotate_quat(matrix, value)
    if data_path_addition == 'location':
        value = rotate_vec3(matrix, value)

    end_keyframe = round((interval_end + sequence_start - interval_start) / frame_time, 0)
    set_new_curves(action, bone_name, data_path, fcurves, starting_keyframe - 1, value, None, None, interpolation_type)
    set_new_curves(action, bone_name, data_path, fcurves, end_keyframe + 1, value, None, None, interpolation_type)

    for time, transformation in transformations.keyframes.items():

        if interval_start <= time <= interval_end:
            real_time = round((time + sequence_start - interval_start) / frame_time, 0)
            value = list(transformation)
            if data_path_addition == 'rotation_quaternion' and value[0] < 0:
                if 0 < bone_name.count("HairBack"):
                    print(value)
                for i in range(len(value)):
                    value[i] = value[i] * -1.0

                if 0 < bone_name.count("HairBack"):
                    print(value)
            if data_path_addition == 'rotation_quaternion':
                value = rotate_quat(matrix, value)
            if data_path_addition == 'location':
                value = rotate_vec3(matrix, value)
            set_new_curves(action, bone_name, data_path, fcurves, real_time, value,
                           h_lefts.get(time), h_rights.get(time), interpolation_type)


def rotate_vec3(matrix: Matrix, value: List[float]):
    vec = Vector(value)
    vec.rotate(matrix)
    value = list(vec)
    return value


def rotate_quat(matrix: Matrix, value: List[float]):
    axis, angle = Quaternion(value).to_axis_angle()
    axis.rotate(matrix)
    quat = Quaternion(axis, angle)
    quat.normalize()
    value = list(quat)
    return value


def add_unanimated_to_bones(action: bpy.types.Action, node: War3Node, bone_name: str):
    loc_interp = 'CONSTANT' if not node.anim_loc else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_loc.interpolation]
    rot_interp = 'CONSTANT' if not node.anim_rot else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_rot.interpolation]
    scale_interp = 'CONSTANT' if not node.anim_scale else constants.INTERPOLATION_NAME_BLEND_NAME[node.anim_scale.interpolation]

    data_path = 'pose.bones["' + bone_name + '"]'
    set_new_curves(action, bone_name, data_path + '.location', [], 0, [0.0, 0.0, 0.0], None, None, loc_interp)
    set_new_curves(action, bone_name, data_path + '.rotation_quaternion', [], 0, [1.0, 0.0, 0.0, 0.0], None, None, rot_interp)
    set_new_curves(action, bone_name, data_path + '.scale', [], 0, [1.0, 1.0, 1.0], None, None, scale_interp)


def set_new_curves(action: bpy.types.Action,
                   bone_name: str,
                   data_path: str,
                   fcurves: List[bpy.types.FCurve],
                   keyframe: float,
                   value: Optional[List[float]],
                   h_left: Optional[List[float]],
                   h_right: Optional[List[float]], interpolation: str = 'CONSTANT'):
    # print("fcurves: ", fcurves)
    for i in range(len(value)):
        if len(fcurves) <= i:
            fcurves_new = action.fcurves.new(data_path, index=i, action_group=bone_name)
            fcurves.append(fcurves_new)
        if value is not None and i < len(value):
            if 0 < bone_name.count("HairBack") and action.name != "all sequences":
                print(action.name, bone_name, "f_curve[" + str(i) + "]:", fcurves[i], " = ", value)
            kf_point = fcurves[i].keyframe_points.insert(keyframe, value[i])
            kf_point.interpolation = interpolation
            if h_left:
                kf_point.handle_left = value[i] + h_left[i]
            if h_right:
                kf_point.handle_left = value[i] + h_right[i]
    return fcurves
