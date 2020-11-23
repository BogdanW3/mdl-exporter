from bpy.types import UIList
from ..operators.WAR3_OT_create_eventobject import WAR3_OT_create_eventobject
from ..operators.WAR3_OT_create_collision_shape import WAR3_OT_create_collision_shape
from ..operators.WAR3_OT_add_anim_sequence import WAR3_OT_add_anim_sequence
import bpy

class VIEW_MT_war3_add(bpy.types.Menu):
    bl_idname = "VIEW_MT_war3_add"
    bl_label = "MDL add"
    # bl_region_type = 'VIEW3D'

    def draw(self, context):
        layout = self.layout
        # layout.separator()
        layout.operator(WAR3_OT_create_eventobject.bl_idname)
        layout.operator(WAR3_OT_create_collision_shape.bl_idname)
        layout.operator(WAR3_OT_add_anim_sequence.bl_idname)
