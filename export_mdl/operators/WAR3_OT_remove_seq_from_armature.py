import bpy


class WAR3_OT_remove_seq_from_armature(bpy.types.Operator):
    bl_idname = 'warcraft_3.remove_sequence_to_armature'
    bl_label = 'Warcraft 3 Remove Sequence to Armature'
    bl_description = 'Warcraft 3 Remove Sequence to Armature'
    bl_options = {'UNDO'}

    def execute(self, context):
        if context.armature:
            warcraft3data = context.armature.warcraft_3
            warcraft3data.sequencesList.remove(warcraft3data.sequencesListIndex)
        return {'FINISHED'}
