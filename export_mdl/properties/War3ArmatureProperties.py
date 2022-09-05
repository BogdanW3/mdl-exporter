import bpy

from export_mdl.properties.War3ArmatureSequenceList import War3ArmatureSequenceList

ACTION_NAME_UNANIMATED = '#UNANIMATED'


def set_animation(arm_property, context: bpy.types.Context):
    animation_name = context.armature.war_3.sequencesList[context.armature.war_3.sequencesListIndex].name
    if len(animation_name) and bpy.data.actions.get(animation_name):
        prepare_action(context, animation_name)
        for action in bpy.data.actions:
            for bpy_object in bpy.context.scene.objects:
                object_animation_name = animation_name + ' ' + bpy_object.name
                if action.name == object_animation_name:
                    if bpy_object.animation_data is None:
                        bpy_object.animation_data_create()
                    bpy_object.animation_data.action = action
    else:
        unanimated = ACTION_NAME_UNANIMATED
        action = bpy.data.actions.get(unanimated, None)
        if action:
            prepare_action(context, unanimated)
            for bpy_object in bpy.context.scene.objects:
                object_action_name = unanimated + ' ' + bpy_object.name
                if bpy.data.actions.get(object_action_name, None):
                    if bpy_object.animation_data is None:
                        bpy_object.animation_data_create()
                    bpy_object.animation_data.action = bpy.data.actions[object_action_name]


def prepare_action(context: bpy.types.Context, animation_name: str):
    armature_object = context.object
    if armature_object.animation_data is None:
        armature_object.animation_data_create()
    bpy_action = bpy.data.actions[animation_name]
    # bpy_action = bpy.data.actions.get(animation_name)
    armature_object.animation_data.action = bpy_action
    bpy.context.scene.frame_start = bpy_action.frame_range[0]
    bpy.context.scene.frame_end = bpy_action.frame_range[1]


class War3ArmatureProperties(bpy.types.PropertyGroup):
    sequencesList: bpy.props.CollectionProperty(type=War3ArmatureSequenceList)
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
