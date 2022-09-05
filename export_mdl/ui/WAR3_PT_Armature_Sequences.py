import bpy


class WAR3_PT_Armature_Sequences(bpy.types.Panel):
    bl_idname = 'WAR3_PT_Armature_Sequences'
    bl_label = 'EE- WarCraft 3'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.armature

    def draw(self, context: bpy.types.Context):
        war3_data = context.armature.war_3
        # print(context, context.__class__)
        layout = self.layout
        layout.label(text='Animations:')
        row = layout.row()
        row.template_list(
            listtype_name='UI_UL_list',
            list_id='name',
            dataptr=war3_data,
            propname='sequencesList',
            active_dataptr=war3_data,
            active_propname='sequencesListIndex',
            rows=2
            )
        col = row.column(align=True)
        col.operator('war_3.add_sequence_to_armature', icon='ADD', text='')
        col.operator('war_3.remove_sequence_from_armature', icon='REMOVE', text='')
