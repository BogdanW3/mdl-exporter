
import bpy

from ..operators.WAR3_OT_generate_from_actions import WAR3_OT_generate_from_actions


class WAR3_MT_sequence_context_menu(bpy.types.Menu):
    bl_idname = "WAR3_MT_sequence_context_menu"
    bl_label = "Sequence Specials"
    # bl_region_type = 'VIEW3D'

    def draw(self, context):
        layout = self.layout

        print("layout.direction", layout.direction)
        print("layout.alignment", layout.alignment)
        print("layout.use_property_decorate", layout.use_property_decorate)

        layout.operator(WAR3_OT_generate_from_actions.bl_idname)
        layout.operator('war_3.add_sequence_to_armature', icon='SORTALPHA', text="Sort")
        layout.operator('war_3.add_sequence_to_armature', icon='ADD', text="add")
        layout.operator('war_3.add_sequence_to_armature', icon='DUPLICATE', text="duplicate")
        layout.operator('war_3.remove_sequence_from_armature', icon='REMOVE', text="remove").type = 'REMOVE'
        layout.operator('war_3.remove_sequence_from_armature', icon='TRASH', text="remove (including action)").type = 'DELETE'

        layout.separator()

        layout.operator('war_3.move_seq_in_list', icon='TRIA_UP_BAR', text="move first").direction = 'FIRST'
        layout.operator('war_3.move_seq_in_list', icon='TRIA_UP', text="move up").direction = 'UP'
        layout.operator('war_3.move_seq_in_list', icon='TRIA_DOWN', text="move down").direction = 'DOWN'
        layout.operator('war_3.move_seq_in_list', icon='TRIA_DOWN_BAR', text="move last").direction = 'LAST'

