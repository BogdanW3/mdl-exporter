from bpy.types import UIList

from ..properties.War3MaterialLayerProperties import HD_SLOT_NAMES


class WAR3_UL_material_layer_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0):
        icons = {
            '0': 'IMAGE_DATA',
            '1': 'TEXTURE',
            '2': 'SHADING_TEXTURE',
            '11': 'FACESEL',
            '36': 'IMAGE_RGB_ALPHA',
            'Tree': 'MESH_CONE'
        }

        icon = icons[item.texture_type] if item.texture_type in icons.keys() else icons['Tree']

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if getattr(data, "mdl_shader", 'AUTO') in ('HD', 'CRYSTAL'):
                # HD layers are texture slots, say which one
                slot = HD_SLOT_NAMES[index] if index < len(HD_SLOT_NAMES) else "Unused"
                split = layout.split(factor=0.35)
                split.label(text=slot)
                split.prop(item, "name", text="", emboss=False, icon=icon)
            else:
                layout.prop(item, "name", text="", emboss=False, icon=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=icon)
