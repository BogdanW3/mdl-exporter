import bpy

from export_mdl.properties.War3ArmatureSequenceListItem import War3ArmatureSequenceListItem

ACTION_NAME_UNANIMATED = '#UNANIMATED'


def set_animation(arm_property, context: bpy.types.Context):
    print("set_animation?", arm_property, context)
    # arm_p: War3ArmatureProperties = arm_property
    # sequences_list = arm_p.sequencesList
    sequences_list = arm_property.sequencesList
    for seq in sequences_list:
        print(seq)
    armature_prop = context.armature.war_3
    seq_prop = armature_prop.sequencesList[armature_prop.sequencesListIndex]
    animation_name = seq_prop.name
    if len(animation_name) and bpy.data.actions.get(animation_name):
        print("has", animation_name)
        prepare_action(context, animation_name, seq_prop.length)
        for action in bpy.data.actions:
            for bpy_object in bpy.context.scene.objects:
                object_animation_name = animation_name + ' ' + bpy_object.name
                if action.name == object_animation_name:
                    if bpy_object.animation_data is None:
                        bpy_object.animation_data_create()
                    bpy_object.animation_data.action = action
    else:
        print("did not find", animation_name)
        action = bpy.data.actions.get(ACTION_NAME_UNANIMATED, None)
        if not action:
            action = bpy.data.actions.new(ACTION_NAME_UNANIMATED)
        if action:
            prepare_action(context, ACTION_NAME_UNANIMATED, 1)
            for bpy_object in bpy.context.scene.objects:
                object_action_name = ACTION_NAME_UNANIMATED + ' ' + bpy_object.name
                if bpy.data.actions.get(object_action_name, None):
                    if bpy_object.animation_data is None:
                        bpy_object.animation_data_create()
                    bpy_object.animation_data.action = bpy.data.actions[object_action_name]


def prepare_action(context: bpy.types.Context, animation_name: str, anim_length):
    armature_object = context.object
    if armature_object.animation_data is None:
        armature_object.animation_data_create()
    bpy_action = bpy.data.actions[animation_name]
    # bpy_action = bpy.data.actions.get(animation_name)
    armature_object.animation_data.action = bpy_action
    # bpy.context.scene.frame_start = bpy_action.frame_range[0]
    # bpy.context.scene.frame_end = bpy_action.frame_range[1]
    print(animation_name, 0, "-", anim_length)
    print("armature_object.animation_data.action:", armature_object.animation_data.action)
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = anim_length


# def set_animation(arm_property, context: bpy.types.Context):
#     print("sequenceList?", context, arm_property)


class War3ArmatureProperties(bpy.types.PropertyGroup):
    sequencesList: bpy.props.CollectionProperty(type=War3ArmatureSequenceListItem)
    sequencesListIndex: bpy.props.IntProperty(update=set_animation)

    @classmethod
    def register(cls):
        bpy.types.Armature.war_3 = bpy.props.PointerProperty(type=War3ArmatureProperties, options={'HIDDEN'})
        # bpy.types.Armature.sequencesList = bpy.props.CollectionProperty(type=War3ArmatureSequenceList)
        # bpy.types.Armature.sequencesListIndex = bpy.props.IntProperty(update=set_animation)

    @classmethod
    def unregister(cls):
        del bpy.types.Armature.war_3
        # del bpy.types.Armature.sequencesList
        # del bpy.types.Armature.sequencesListIndex
