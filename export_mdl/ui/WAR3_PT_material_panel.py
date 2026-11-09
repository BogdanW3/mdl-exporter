import bpy

from ..properties.War3MaterialLayerProperties import HD_SLOT_NAMES


def sub_panel(layout: bpy.types.UILayout, idname: str, title: str, default_closed: bool = True):
    """A collapsible section (Blender 4.1+), or a plain column on older versions. Returns None when collapsed."""
    if hasattr(layout, "panel"):
        header, body = layout.panel(idname, default_closed=default_closed)
        header.label(text=title)
        return body
    col = layout.column()
    col.label(text=title)
    return col


class WAR3_PT_material_panel(bpy.types.Panel):
    """Creates a material editor Panel in the Material window"""
    bl_idname = "WAR3_PT_material_panel"
    bl_label = "Warcraft 3 Material"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'material'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.active_material is not None

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        mat = context.active_object.active_material
        shader = getattr(mat, "mdl_shader", 'AUTO')
        hd = shader in ('HD', 'CRYSTAL')

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(mat, "priority_plane")
        col.prop(mat, "mdl_shader")
        if hd:
            col.label(text="HD needs version 900 or newer, layers are the texture slots", icon='INFO')

        layout.separator()
        layout.label(text="Texture Slots (v900+)" if hd else "Layers")

        layers = getattr(mat, "mdl_layers", None)
        index = getattr(mat, "mdl_layer_index", None)
        if layers is None or index is None:
            return

        row = layout.row()
        row.template_list("WAR3_UL_material_layer_list", "", mat, "mdl_layers", mat, "mdl_layer_index", rows=2)

        col = row.column(align=True)
        col.operator("war_3.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("war_3.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("war_3.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("war_3.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        if not len(layers):
            box = layout.box()
            col = box.column(align=True)
            col.label(text="No layers: the textures are read from the node tree", icon='NODETREE')
            if hd:
                col.label(text="Principled BSDF inputs used for each slot:")
                col.label(text="    Diffuse: Base Color    Normal: Normal")
                col.label(text="    ORM: Roughness/Metallic    Emissive: Emission")
                box.operator("war_3.setup_hd_nodes", icon='NODETREE')
            else:
                col.label(text="Base Color gives the texture. Add layers to set it here instead")
            return
        if not 0 <= index < len(layers):
            return

        active_layer = layers[index]
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False

        if hd:
            slot = HD_SLOT_NAMES[index] if index < len(HD_SLOT_NAMES) else "Unused"
            col.label(text="Slot %d: %s" % (index, slot), icon='TEXTURE')
        col.prop(active_layer, "name")
        col.separator()
        col.prop(active_layer, "texture_type")
        if active_layer.texture_type == '0':  # Image texture
            row = col.row(align=True)
            row.prop(active_layer, "path", text="Texture Path")
            row.operator("object.search_texture", text="", icon='VIEWZOOM').target = 'Material'
        elif active_layer.texture_type == '36':
            col.prop(active_layer, "replaceable_id")

        # HD materials take their filter mode, flags and animated values from the first slot
        if hd and index != 0:
            col.label(text="Filter mode and flags come from slot 0 (Diffuse)", icon='INFO')
            return

        col.separator()
        col.prop(active_layer, "filter_mode")
        col.prop(active_layer, "alpha")

        body = sub_panel(layout, "WAR3_material_flags", "Flags", default_closed=False)
        if body:
            flow = body.grid_flow(columns=2, even_columns=True)
            for prop in ("unshaded", "unfogged", "two_sided", "sphere_env_map",
                         "no_depth_test", "no_depth_set", "wrap_width", "wrap_height"):
                flow.prop(active_layer, prop)
            if hd:
                for prop in ("unlit", "back_faces_for_shadows", "ambient_occlusion"):
                    flow.prop(active_layer, prop)

        body = sub_panel(layout, "WAR3_material_hd", "Emissive & Fresnel (v900+)")
        if body:
            body.use_property_split = True
            body.prop(active_layer, "emissive_gain")
            body.prop(active_layer, "fresnel_color")
            body.prop(active_layer, "fresnel_opacity")
            body.prop(active_layer, "fresnel_team_color")
            body.label(text="Fresnel needs v1000+, emissive gain v900+")
