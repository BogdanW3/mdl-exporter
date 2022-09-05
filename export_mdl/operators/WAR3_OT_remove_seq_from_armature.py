import bpy


class WAR3_OT_remove_seq_from_armature(bpy.types.Operator):
    bl_idname = 'war_3.remove_sequence_from_armature'
    bl_label = 'EE-Warcraft 3 Remove Sequence to Armature'
    bl_description = 'Warcraft 3 Remove Sequence to Armature'
    bl_options = {'UNDO'}

    def execute(self, context):
        if context.armature:
            war3_data = context.armature.war_3
            war3_data.sequencesList.remove(war3_data.sequencesListIndex)
        return {'FINISHED'}
