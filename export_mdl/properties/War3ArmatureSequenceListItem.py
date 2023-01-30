import bpy


def set_animation_name(seq_prop, context: bpy.types.Context):
    # armature_prop = context.armature.war_3
    # seq_prop = armature_prop.sequencesList[armature_prop.sequencesListIndex]
    # print("setting name?", seq_prop.name, context)
    animation_name = seq_prop.action_name
    if seq_prop.name != animation_name:
        actions = bpy.data.actions
        bpy_data_action = actions.get(animation_name)
        # bpy_data_action:bpy.types.Action = actions.get(animation_name)
        if bpy_data_action:
            bpy_data_action.name = seq_prop.name
    seq_prop.action_name = seq_prop.name
        # if len(animation_name) and bpy_data_action:
        #     prepare_action(context, animation_name, seq_prop.length)
        #     for action in bpy.data.actions:
        #         for bpy_object in bpy.context.scene.objects:
        #             object_animation_name = animation_name + ' ' + bpy_object.name
        #             if action.name == object_animation_name:
        #                 if bpy_object.animation_data is None:
        #                     bpy_object.animation_data_create()
        #                 bpy_object.animation_data.action = action



def set_animation(seq_prop, context: bpy.types.Context):
    # armature_prop = context.armature.war_3
    # seq_prop = armature_prop.sequencesList[armature_prop.sequencesListIndex]
    # print("setting length?", seq_prop.action_name, seq_prop.length)
    animation_name = seq_prop.action_name
    if len(animation_name) and bpy.data.actions.get(animation_name):
        prepare_action(context, animation_name, seq_prop.length)
        for action in bpy.data.actions:
            for bpy_object in bpy.context.scene.objects:
                object_animation_name = animation_name + ' ' + bpy_object.name
                if action.name == object_animation_name:
                    if bpy_object.animation_data is None:
                        bpy_object.animation_data_create()
                    bpy_object.animation_data.action = action
                    print(bpy_object.animation_data.action)


def prepare_action(context: bpy.types.Context, animation_name: str, anim_length):
    armature_object = context.object
    if armature_object.animation_data is None:
        armature_object.animation_data_create()
    bpy_action = bpy.data.actions[animation_name]
    # bpy_action = bpy.data.actions.get(animation_name)
    armature_object.animation_data.action = bpy_action
    # print("seqItem, action: ", armature_object.animation_data.action)
    # bpy.context.scene.frame_start = bpy_action.frame_range[0]
    # bpy.context.scene.frame_end = bpy_action.frame_range[1]
    # print(animation_name, 0, "-", anim_length)
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = anim_length


class War3ArmatureSequenceListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        default="new Sequence",
        update=set_animation_name
    )
    action_name: bpy.props.StringProperty(
        name="ActionName",
    )
    length: bpy.props.IntProperty(
        name="Length",
        min=0,
        default=150,
        update=set_animation
    )
    non_looping: bpy.props.BoolProperty(
        name="NonLooping",
        default=False
    )

