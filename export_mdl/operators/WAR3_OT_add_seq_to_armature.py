from typing import Optional

import bpy

from ..action_compat import assign_action


class WAR3_OT_add_seq_to_armature(bpy.types.Operator):
    bl_idname = 'war_3.add_sequence_to_armature'
    bl_label = 'Add Sequence'
    bl_description = 'Add a sequence with a new action to the armature'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.armature

    def execute(self, context):
        armature_object: Optional[bpy.types.Armature] = context.object
        armature: Optional[bpy.types.Armature] = context.armature
        if armature and armature_object:
            war3_data = armature.war_3
            sequence = war3_data.sequencesList.add()
            bpy_action = bpy.data.actions.new(sequence.name)
            sequence.name = bpy_action.name
            sequence.action_name = bpy_action.name

            if armature_object.animation_data is None:
                armature_object.animation_data_create()

            assign_action(armature_object, bpy_action)

            print("addSeq - ", bpy_action, 0, "-", sequence.length)
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = sequence.length
            war3_data.sequencesListIndex = len(war3_data.sequencesList)-1

        return {'FINISHED'}
