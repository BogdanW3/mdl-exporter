from typing import List, Dict

import bpy
from bpy.app.handlers import persistent

from ..properties.War3SequenceProperties import War3SequenceProperties


def set_current_sequence(prop: 'War3SequencesProperties', context: bpy.types.Context):
    bpy.context.scene.frame_start = prop.mdl_sequences[prop.mdl_sequence_index].start
    bpy.context.scene.frame_end = prop.mdl_sequences[prop.mdl_sequence_index].end


class War3SequencesProperties(bpy.types.PropertyGroup):
    mdl_sequences: bpy.props.CollectionProperty(
        type=War3SequenceProperties,
        options={'HIDDEN'})
    mdl_sequence_index: bpy.props.IntProperty(
        name="Sequence index",
        description="",
        default=0,
        update=set_current_sequence,
        options={'HIDDEN'})

    @classmethod
    def register(cls):
        print("ugg1")
        bpy.types.Scene.war3_mdl_sequences = bpy.props.PointerProperty(
            type=War3SequencesProperties,
            options={'HIDDEN'})
        print("ugg2")
        bpy.types.WindowManager.mdl_sequence_refreshing = bpy.props.BoolProperty(
            name="sequence refreshing",
            description="",
            default=False,
            options={'HIDDEN'})

        if sequence_changed_handler not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(sequence_changed_handler)

    @classmethod
    def unregister(cls):
        if sequence_changed_handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(sequence_changed_handler)

        del bpy.types.WindowManager.mdl_sequence_refreshing
        del bpy.types.Scene.war3_mdl_sequences


@persistent
def sequence_changed_handler(self):
    print("sequence_changed_handler\n\n")
    context = bpy.context
    # Prevent recursion
    if context.window_manager.mdl_sequence_refreshing:
        return

    context.window_manager.mdl_sequence_refreshing = True

    war3_mdl_sequences = context.scene.war3_mdl_sequences
    sequences = war3_mdl_sequences.mdl_sequences

    markers: Dict[str, List[int]] = {}
    for tlm in context.scene.timeline_markers:
        marker_instances = markers.get(tlm.name, [])
        marker_instances.append(tlm.frame)
        markers[tlm.name] = marker_instances

    for marker, frames in markers.items():
        if len(frames) == 2 and marker not in sequences:
            s = sequences.add()
            s.seq_name = marker
            if any(tag in s.seq_name.lower() for tag in ['attack', 'death', 'decay']):
                s.non_looping = True

    for sequence in sequences.values():
        if sequence.seq_name not in markers:
            index = sequences.find(sequence.seq_name)
            if index <= war3_mdl_sequences.mdl_sequence_index:
                war3_mdl_sequences.mdl_sequence_index = index - 1
            sequences.remove(index)

    context.window_manager.mdl_sequence_refreshing = False
