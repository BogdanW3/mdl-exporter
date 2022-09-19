from typing import Optional

import bpy


class WAR3_OT_move_seq_down(bpy.types.Operator):
    bl_idname = 'war_3.move_seq_own'
    bl_label = 'Warcraft 3 Move Sequence Down'
    bl_description = 'Warcraft 3 Move Sequence In List'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.armature

    def execute(self, context):
        armature_object: Optional[bpy.types.Armature] = context.object
        armature: Optional[bpy.types.Armature] = context.armature
        if armature and armature_object:
            war3_data = armature.war_3
            if war3_data.sequencesListIndex < len(war3_data.sequencesList)-1:
                # sequences_list: bpy.types.Collection = war3_data.sequencesList
                sequences_list = war3_data.sequencesList
                print("sequences_list:", sequences_list, isinstance(sequences_list, bpy.types.Collection))
                sequences_list.move(war3_data.sequencesListIndex, war3_data.sequencesListIndex+1)
                war3_data.sequencesListIndex = war3_data.sequencesListIndex+1

        return {'FINISHED'}
