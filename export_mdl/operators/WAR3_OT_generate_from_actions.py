import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator


class WAR3_OT_generate_from_actions(Operator):
    """Generate Warcraft 3 animation sequences from existing actions"""
    bl_idname = "war_3.generate_from_actions"
    bl_label = "Warcraft 3 Generate Sequences"
    bl_description = 'Warcraft 3 Generate Sequences From Actions'
    bl_options = {'UNDO'}

    def execute(self, context: bpy.types.Context):
        # scene = context.window.scene
        # sequences = scene.mdl_sequences
        #
        # s = sequences.add()
        # s.name = self.name
        # s.rarity = self.rarity
        # s.non_looping = self.non_looping
        #
        # scene.mdl_sequence_index = len(sequences) - 1
        if context.armature:
            war3_data = context.armature.war_3
            sequences_list = war3_data.sequencesList
            sequence_index = war3_data.sequencesListIndex
            sequences_names = set(seq.name for seq in sequences_list)

            for action in bpy.data.actions:
                if action.name not in sequences_names:
                    sequence = war3_data.sequencesList.add()
                    sequence.name = action.name
                    sequence.length = action.frame_range[1] - action.frame_range[0]
            war3_data.sequencesListIndex = sequence_index

        return {'FINISHED'}
