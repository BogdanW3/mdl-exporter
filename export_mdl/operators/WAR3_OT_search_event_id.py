from bpy.props import EnumProperty
from bpy.types import Operator

# from .operators import event_items
from ..properties.properties import War3EventTypesContainer

war3_event_types = War3EventTypesContainer()


def event_items(self, context):
    return war3_event_types.enums[context.window_manager.events.event_type]


class WAR3_OT_search_event_id(Operator):
    bl_idname = "object.search_eventid"
    bl_label = "Search"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_property = "ids"

    ids: EnumProperty(
                name="Event ID",
                items=event_items,
            )

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        context.window_manager.events.event_id = self.ids
        return {'FINISHED'}
