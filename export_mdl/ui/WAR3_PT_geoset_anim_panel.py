import bpy

from ..geoset_preview import has_geoset_preview


class WAR3_PT_geoset_anim_panel(bpy.types.Panel):
    """Geoset animation (visibility and tint per sequence) of a mesh object"""
    bl_idname = "WAR3_PT_geoset_anim_panel"
    bl_label = "Warcraft 3 Geoset Animation"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'object'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and hasattr(obj, "mdl_geoset")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True  # Shows the keyframe dots
        geoset = context.active_object.mdl_geoset
        col = layout.column()
        col.prop(geoset, "alpha")
        col.prop(geoset, "color")
        layout.label(text="Keyframe on the scene timeline, at your sequence markers", icon='INFO')
        if not has_geoset_preview(context.active_object):
            layout.operator("war_3.geoset_preview", icon='HIDE_OFF')
