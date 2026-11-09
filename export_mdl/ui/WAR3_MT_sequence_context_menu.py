import bpy

from ..operators.WAR3_OT_generate_from_actions import WAR3_OT_generate_from_actions


class WAR3_MT_sequence_context_menu(bpy.types.Menu):
    bl_idname = "WAR3_MT_sequence_context_menu"
    bl_label = "Sequence Specials"

    def draw(self, context):
        layout = self.layout

        layout.operator(WAR3_OT_generate_from_actions.bl_idname)
        layout.operator('war_3.sort_sequences', icon='SORTALPHA', text="Sort by Name")
        layout.operator('war_3.add_sequence_to_armature', icon='ADD', text="Add")
        layout.operator('war_3.duplicate_sequence', icon='DUPLICATE', text="Duplicate")
        layout.operator('war_3.remove_sequence_from_armature', icon='REMOVE', text="Remove").type = 'REMOVE'
        layout.operator('war_3.remove_sequence_from_armature', icon='TRASH', text="Remove (Including Action)").type = 'DELETE'

        layout.separator()

        layout.operator('war_3.move_seq_in_list', icon='TRIA_UP_BAR', text="Move to Top").direction = 'FIRST'
        layout.operator('war_3.move_seq_in_list', icon='TRIA_UP', text="Move Up").direction = 'UP'
        layout.operator('war_3.move_seq_in_list', icon='TRIA_DOWN', text="Move Down").direction = 'DOWN'
        layout.operator('war_3.move_seq_in_list', icon='TRIA_DOWN_BAR', text="Move to Bottom").direction = 'LAST'
