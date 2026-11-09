from typing import Optional

import bpy


class WAR3_OT_sort_sequences(bpy.types.Operator):
    bl_idname = 'war_3.sort_sequences'
    bl_label = 'Sort Sequences'
    bl_description = 'Sort the armature\'s sequences by name'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.armature is not None and 1 < len(context.armature.war_3.sequencesList)

    def execute(self, context):
        war3_data = context.armature.war_3
        sequences = war3_data.sequencesList
        active = sequences[war3_data.sequencesListIndex].name \
            if 0 <= war3_data.sequencesListIndex < len(sequences) else None

        # Selection sort with move(), the only way to reorder a collection in place
        for target in range(len(sequences)):
            names = [sequence.name.lower() for sequence in sequences]
            smallest = min(range(target, len(sequences)), key=lambda i: names[i])
            if smallest != target:
                sequences.move(smallest, target)

        if active is not None:
            # Index updates assign the action, so only set it when it changed
            new_index = next(i for i, sequence in enumerate(sequences) if sequence.name == active)
            if new_index != war3_data.sequencesListIndex:
                war3_data.sequencesListIndex = new_index
        return {'FINISHED'}


class WAR3_OT_duplicate_sequence(bpy.types.Operator):
    bl_idname = 'war_3.duplicate_sequence'
    bl_label = 'Duplicate Sequence'
    bl_description = 'Copy the active sequence and its action'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.armature is None:
            return False
        war3_data = context.armature.war_3
        return 0 <= war3_data.sequencesListIndex < len(war3_data.sequencesList)

    def execute(self, context):
        war3_data = context.armature.war_3
        sequences = war3_data.sequencesList
        source_index = war3_data.sequencesListIndex
        source = sequences[source_index]

        source_action: Optional[bpy.types.Action] = bpy.data.actions.get(source.action_name)
        if source_action is not None:
            name = source_action.copy().name
        else:
            name = source.name + " copy"

        sequence = sequences.add()
        # Set the action name first, so the name update doesn't rename anything
        sequence.action_name = name
        sequence.name = name
        for prop in source.bl_rna.properties:
            if prop.identifier not in {'rna_type', 'name', 'action_name'} and not prop.is_readonly:
                setattr(sequence, prop.identifier, getattr(source, prop.identifier))

        sequences.move(len(sequences) - 1, source_index + 1)
        war3_data.sequencesListIndex = source_index + 1
        return {'FINISHED'}
