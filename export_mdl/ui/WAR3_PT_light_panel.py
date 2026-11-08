import bpy
from bpy.props import PointerProperty
from bpy.types import Panel

from ..properties import War3LightSettings


class WAR3_PT_light_panel(Panel):
    """Displays light properties in the lamp panel"""
    bl_idname = "WAR3_PT_light_panel"
    bl_label = "MDL Light Settings"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'data'

    @classmethod
    def register(cls):
        bpy.types.Light.mdl_light = PointerProperty(type=War3LightSettings.War3LightSettings)

    @classmethod
    def unregister(cls):
        del bpy.types.Light.mdl_light

    @classmethod
    def poll(self,context):
        obj = context.active_object
        return obj is not None and obj.type in ('LAMP', 'LIGHT')

    def draw(self, context):
        layout = self.layout
        data = context.active_object.data.mdl_light

        layout.prop(data, "light_type")
        layout.prop(data, "atten_start")
        layout.prop(data, "atten_end")
        if data.light_type != 'Ambient':
            layout.prop(data, "color")
            layout.prop(data, "intensity")
        else:
            layout.prop(data, "amb_color")
            layout.prop(data, "amb_intensity")

        if hasattr(layout, "panel"):  # Blender 4.1+
            header, body = layout.panel("WAR3_PT_light_panel_shadows", default_closed=True)
            header.label(text="Shadows & Falloff (v1200+)")
        else:
            body = layout.box()
            body.label(text="Shadows & Falloff (v1200+)")
        if body:
            body.prop(data, "shadow_intensity")
            body.prop(data, "shadow_casting")
            col = body.column()
            col.active = data.shadow_casting
            col.prop(data, "shadow_casting_start")
            col.prop(data, "shadow_casting_end")
            body.label(text="Falloff (v1600+)")
            body.prop(data, "quadratic_falloff")
            body.prop(data, "linear_falloff")
            body.prop(data, "damping")
