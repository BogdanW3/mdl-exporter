from bpy.props import EnumProperty
from bpy.types import Operator


class WAR3_OT_search_event_type(Operator):
    """Search list of Warcraft 3 internal events"""
    bl_idname = "object.search_event_type"
    bl_label = "Search"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_property = "types"

    types: EnumProperty(
                name="Event Type",
                items=[('SND', "Sound", ""),
                       ('FTP', "Footprint", ""),
                       ('SPN', "Spawned Object", ""),
                       ('SPL', "Splat", ""),
                       ('UBR', "UberSplat", "")],
                default='SND',
            )

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        context.window_manager.events.event_type = self.types
        return {'FINISHED'}
