import bpy


class WAR3_OT_add_seq_to_armature(bpy.types.Operator):
    bl_idname = 'war_3.add_sequence_to_armature'
    bl_label = 'Warcraft 3 Add Sequence to Armature'
    bl_description = 'Warcraft 3 Add Sequence to Armature'
    bl_options = {'UNDO'}

    def execute(self, context):
        if context.armature:
            war3_data = context.armature.war_3
            sequence = war3_data.sequencesList.add()
            sequence.name = '#UNANIMATED'
        return {'FINISHED'}
