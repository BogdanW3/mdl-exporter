import bpy


class WAR3_OT_remove_seq_from_armature(bpy.types.Operator):
    bl_idname = 'war_3.remove_sequence_from_armature'
    bl_label = 'Warcraft 3 Remove Sequence from Armature'
    bl_description = 'Warcraft 3 Remove Sequence to Armature'
    bl_options = {'UNDO'}

    type: bpy.props.EnumProperty(
        name="Type",
        items=[('REMOVE', "Remove", ""),
               ('DELETE', "Delete", "")],
        default='REMOVE'
    )

    def execute(self, context):
        if context.armature:
            war3_data = context.armature.war_3
            if self.type == 'DELETE':
                seq_prop = war3_data.sequencesList[war3_data.sequencesListIndex]
                animation_name = seq_prop.name
                bpy_action = bpy.data.actions.get(animation_name)
                bpy.data.actions.remove(bpy_action)

            war3_data.sequencesList.remove(war3_data.sequencesListIndex)
            if war3_data.sequencesListIndex < len(war3_data.sequencesList):
                war3_data.sequencesListIndex = war3_data.sequencesListIndex
            elif 0 < war3_data.sequencesListIndex:
                war3_data.sequencesListIndex = war3_data.sequencesListIndex-1

        return {'FINISHED'}
