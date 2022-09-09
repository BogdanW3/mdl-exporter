from typing import List, Tuple

import bpy
from ..War3AnimationAction import War3AnimationAction
from ...properties.War3SequenceProperties import War3SequenceProperties


def get_actions(f2ms: float, bpy_actions: List[bpy.types.Action], use_actions: bool,
                mdl_sequences: List[War3SequenceProperties]) \
        -> Tuple[List[War3AnimationAction], List[bpy.types.Action]]:
    sequences = []
    actions = []

    for action in bpy_actions:
        if action.name != "all sequences" and action.name != "#UNANIMATED" and use_actions:
            sequence = War3AnimationAction(action.name, action.frame_range[0] * f2ms,
                                           action.frame_range[1] * f2ms, False, 270)
            sequences.append(sequence)
            actions.append(action)
        elif action.name == "all sequences" and not use_actions:
            for mdl_sequence in mdl_sequences:
                # print("mdl_sequence is wc3_seq_prop: ", isinstance(mdl_sequence, War3SequenceProperties))
                # print("mdl_sequence: ", mdl_sequence)
                sequence = War3AnimationAction(mdl_sequence.name, mdl_sequence.start * f2ms, mdl_sequence.end * f2ms,
                                               mdl_sequence.non_looping, mdl_sequence.move_speed, mdl_sequence.rarity)
                sequences.append(sequence)
            actions.append(action)
            break

    if len(sequences) == 0:
        sequences.append(War3AnimationAction("Stand", 0, 1000))

    sequences.sort(key=lambda x: x.start)
    if use_actions:
        space_actions(sequences)

    return sequences, actions


def space_actions(sequence_list: List[War3AnimationAction]):
    last_action_frame = 0
    action_spacing = 10
    for sequence in sequence_list:
        sequence.start = sequence.start + last_action_frame + action_spacing
        sequence.end = sequence.end + last_action_frame + action_spacing
        last_action_frame = sequence.end
