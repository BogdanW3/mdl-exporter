from bpy.types import Panel


class WAR3_PT_sequences_panel(Panel):
    """Creates a sequence editor Panel in the Scene window"""
    bl_idname = "WAR3_PT_sequences_panel"
    bl_label = "Warcraft 3 Sequences"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'scene'

    @classmethod
    def poll(cls, context):
        war3_mdl_sequences = context.scene.war3_mdl_sequences
        return war3_mdl_sequences.mdl_sequences is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        war3_mdl_sequences = getattr(scene, "war3_mdl_sequences", None)
        # print("war3_mdl_sequences: ", war3_mdl_sequences, isinstance(war3_mdl_sequences, War3SequencesProperties),
        #       ", type:", type(war3_mdl_sequences), ", index:", war3_mdl_sequences.mdl_sequence_index)
        # if isinstance(war3_mdl_sequences, War3SequencesProperties):

        index = war3_mdl_sequences.mdl_sequence_index
        sequences = war3_mdl_sequences.mdl_sequences

        layout.operator("war_3.add_anim_sequence", text="Add Sequence")

        if sequences is not None:
            row = layout.row()
            row.template_list(
                listtype_name='WAR3_UL_sequence_list',
                list_id='name',
                dataptr=war3_mdl_sequences,
                propname='mdl_sequences',
                active_dataptr=war3_mdl_sequences,
                active_propname='mdl_sequence_index',
                rows=2
            )
        if sequences is not None and 0 <= index < len(sequences):
            active_sequence = sequences[index]

            col = layout.column(align=True)
            col.prop(active_sequence, "name_display")
            col.separator()

            row = layout.row()
            col = row.column()
            col.label(text="Start")
            col = row.column()
            col.label(text="End")

            row = layout.row()
            col = row.column()
            col.enabled = False
            col.prop(active_sequence, "start")
            col = row.column()
            col.enabled = False
            col.prop(active_sequence, "end")

            col.separator()

            col = layout.column()
            col.prop(active_sequence, "rarity")
            col.separator()
            if 'walk' in active_sequence.name.lower():
                col.prop(active_sequence, "move_speed")
                col.separator()
            col.prop(active_sequence, "non_looping")
