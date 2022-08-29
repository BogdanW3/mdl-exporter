import bpy


class WAR3_OT_add_seq_to_armature(bpy.types.Operator):
    bl_idname = 'warcraft_3.add_sequence_to_armature'
    bl_label = 'Warcraft 3 Add Sequence to Armature'
    bl_description = 'Warcraft 3 Add Sequence to Armature'
    bl_options = {'UNDO'}

    def execute(self, context):
        if context.armature:
            warcraft3data = context.armature.warcraft_3
            sequence = warcraft3data.sequencesList.add()
            sequence.name = '#UNANIMATED'
        return {'FINISHED'}
