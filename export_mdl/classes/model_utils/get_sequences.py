from typing import List

from ..War3AnimationSequence import War3AnimationSequence
from ...properties.War3SequenceProperties import War3SequenceProperties


def get_sequences(f2ms: float, mdl_sequences: List[War3SequenceProperties]):
    sequences = []

    # print("mdl_sequences: ", mdl_sequences)
    # print("mdl_sequences is list: ", isinstance(mdl_sequences, List))
    for mdl_sequence in mdl_sequences:
        # print("mdl_sequence is wc3_seq_prop: ", isinstance(mdl_sequence, War3SequenceProperties))
        # print("mdl_sequence: ", mdl_sequence)
        sequence = War3AnimationSequence(mdl_sequence.name, mdl_sequence.start * f2ms, mdl_sequence.end * f2ms,
                                         mdl_sequence.non_looping, mdl_sequence.move_speed, mdl_sequence.rarity)
        sequences.append(sequence)

    if len(sequences) == 0:
        sequences.append(War3AnimationSequence("Stand", 0, 3333))

    sequences.sort(key=lambda x: x.start)

    return sequences
