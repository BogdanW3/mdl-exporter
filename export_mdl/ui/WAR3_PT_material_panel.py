import bpy

from ..hd_slots import HD_SLOT_NAMES, is_default


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
        if hasattr(mat, "mdl_constant_color"):
            col.prop(mat, "mdl_constant_color")
        col.prop(mat, "mdl_shader")
        if hd:
            col.label(text="HD needs version 900 or newer", icon='INFO')

        layout.separator()
        layout.label(text="Texture Slots (v900+)" if hd else "Layers")

        layers = getattr(mat, "mdl_layers", None)
        index = getattr(mat, "mdl_layer_index", None)
        if layers is None or index is None:
            return

        row = layout.row()
        row.template_list("WAR3_UL_material_layer_list", "", mat, "mdl_layers", mat, "mdl_layer_index", rows=2)

        col = row.column(align=True)
        if hd:
            # The slots are fixed; only layers past the sixth (which the shader doesn't use) can go
            if index >= len(HD_SLOT_NAMES):
                col.operator("war_3.list_action", icon='REMOVE', text="").action = 'REMOVE'
        else:
            col.operator("war_3.list_action", icon='ADD', text="").action = 'ADD'
            col.operator("war_3.list_action", icon='REMOVE', text="").action = 'REMOVE'
            col.separator()
            col.operator("war_3.list_action", icon='TRIA_UP', text="").action = 'UP'
            col.operator("war_3.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        if hd and len(layers) < len(HD_SLOT_NAMES):
            box = layout.box()
            box.label(text="%d of the %d texture slots are set" % (len(layers), len(HD_SLOT_NAMES)), icon='ERROR')
            if not len(layers):
                box.label(text="Until then the textures are read from the node tree")
            box.operator("war_3.hd_slots", text="Fill Texture Slots", icon='TEXTURE').action = 'FILL'
            box.operator("war_3.setup_hd_nodes", icon='NODETREE')
            if not len(layers):
                return

        if not len(layers):
            box = layout.box()
            col = box.column(align=True)
            col.label(text="No layers: the textures are read from the node tree", icon='NODETREE')
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
        if hd and index < len(HD_SLOT_NAMES):
            row = col.row(align=True)
            if is_default(active_layer, index):
                row.label(text="The game's default texture for this slot")
            else:
                row.operator("war_3.hd_slots", text="Use Default", icon='LOOP_BACK').action = 'DEFAULT'
            if index != 4:  # (Team color is always replaceable id 1)
                row.operator("war_3.hd_slots", text="From Node Tree", icon='NODETREE').action = 'NODES'

        if (not hd or index == 0) and mat.node_tree is not None:
            row = col.row(align=True)
            row.prop_search(active_layer, "uv_node", mat.node_tree, "nodes", text="Texture Animation")
            if not active_layer.uv_node:
                row.operator("war_3.add_uv_animation", text="", icon='ADD')

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
