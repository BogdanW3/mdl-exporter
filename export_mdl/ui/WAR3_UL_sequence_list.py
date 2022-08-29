from bpy.types import UIList, UILayout, Context


class WAR3_UL_sequence_list(UIList):
    # def draw_item(self,
    #               context: 'Context',
    #               layout: 'UILayout',
    #               data: 'AnyType',
    #               item: 'AnyType',
    #               icon: int,
    #               active_data: 'AnyType',
    #               active_property: str,
    #               index: int = 0,
    #               flt_flag: int = 0):
    def draw_item(self, context: Context, layout: UILayout, data, item, icon: int, active_data, propname) -> None:
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon='TIME')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value='TIME')
