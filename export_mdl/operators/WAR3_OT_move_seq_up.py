from typing import Optional

import bpy


class WAR3_OT_move_seq_up(bpy.types.Operator):
    bl_idname = 'war_3.move_seq_up'
    bl_label = 'Warcraft 3 Move Sequence Up'
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
            if 0 < war3_data.sequencesListIndex:
                # sequences_list: bpy.types.Collection = war3_data.sequencesList
                sequences_list = war3_data.sequencesList
                print("sequences_list:", sequences_list, isinstance(sequences_list, bpy.types.Collection))
                sequences_list.move(war3_data.sequencesListIndex, war3_data.sequencesListIndex-1)
                war3_data.sequencesListIndex = war3_data.sequencesListIndex-1


                # bpy_action = bpy.data.actions.new(sequence.name)
                # sequence.name = bpy_action.name
                # sequence.action_name = bpy_action.name
                #
                # if armature_object.animation_data is None:
                #     armature_object.animation_data_create()
                #
                # armature_object.animation_data.action = bpy_action
                #
                # print("addSeq - ", bpy_action, 0, "-", sequence.length)
                # bpy.context.scene.frame_start = 0
                # bpy.context.scene.frame_end = sequence.length
                # war3_data.sequencesListIndex = len(sequences_list) - 1

        return {'FINISHED'}
