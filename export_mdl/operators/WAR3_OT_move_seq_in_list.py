from typing import Optional

import bpy


class WAR3_OT_move_seq_in_list(bpy.types.Operator):
    bl_idname = 'war_3.move_seq_in_list'
    bl_label = 'Warcraft 3 Move Sequence In List'
    # bl_description = 'Warcraft 3 Move Sequence In List'
    bl_options = {'UNDO'}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[('FIRST', "First", ""),
               ('UP', "Up", ""),
               ('DOWN', "Down", ""),
               ('LAST', "Last", "")],
        default='UP'
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.armature

    def execute(self, context):
        armature_object: Optional[bpy.types.Armature] = context.object
        armature: Optional[bpy.types.Armature] = context.armature
        if armature and armature_object:
            war3_data = armature.war_3
            new_index: int = -1
            if self.direction == 'FIRST':
                new_index = 0
            elif self.direction == 'UP':
                new_index = war3_data.sequencesListIndex - 1
            elif self.direction == 'DOWN':
                new_index = war3_data.sequencesListIndex + 1
            elif self.direction == 'LAST':
                new_index = len(war3_data.sequencesList)-1

            if 0 <= new_index < len(war3_data.sequencesList):
                sequences_list = war3_data.sequencesList
                # print("sequences_list:", sequences_list, isinstance(sequences_list, bpy.types.Collection))
                sequences_list.move(war3_data.sequencesListIndex, new_index)
                war3_data.sequencesListIndex = new_index

        return {'FINISHED'}
