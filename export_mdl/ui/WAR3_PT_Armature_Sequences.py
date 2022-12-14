import bpy


class WAR3_PT_Armature_Sequences(bpy.types.Panel):
    """Add a Warcraft 3 animation sequence using actions"""
    bl_idname = 'WAR3_PT_Armature_Sequences'
    bl_label = 'WarCraft 3 Actions'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.armature

    def draw(self, context: bpy.types.Context):
        war3_data = context.armature.war_3
        layout = self.layout
        layout.label(text="Animations:")
        row = layout.row()
        row.template_list(
            listtype_name='WAR3_UL_sequence_list',
            list_id='name',
            dataptr=war3_data,
            propname='sequencesList',
            active_dataptr=war3_data,
            active_propname='sequencesListIndex',
            rows=2
        )
        # row.se
        col = row.column(align=True)
        col.operator('war_3.add_sequence_to_armature', icon='ADD', text="")
        col.operator('war_3.remove_sequence_from_armature', icon='REMOVE', text="")
        col.separator()

        col.menu("WAR3_MT_sequence_context_menu", icon='DOWNARROW_HLT', text="")
        col.separator()
        col.operator('war_3.move_seq_in_list', icon='TRIA_UP', text="").direction = 'UP'
        col.operator('war_3.move_seq_in_list', icon='TRIA_DOWN', text="").direction = 'DOWN'

        if war3_data.sequencesListIndex < len(war3_data.sequencesList):
            if war3_data.sequencesList[war3_data.sequencesListIndex].name != '#UNANIMATED':
                # layout.prop(war3_data, "color")
                layout.prop(war3_data.sequencesList[war3_data.sequencesListIndex], 'length')
            layout.prop(war3_data.sequencesList[war3_data.sequencesListIndex], 'name')
            if war3_data.sequencesList[war3_data.sequencesListIndex].name != '#UNANIMATED':
                layout.prop(war3_data.sequencesList[war3_data.sequencesListIndex], "non_looping")
            # settings_row = layout.row()


    # def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    #     war3_data = context.armature.war_3

