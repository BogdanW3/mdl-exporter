from ..War3AnimationSequence import War3AnimationSequence


# def get_sequences(f2ms: float, mdl_sequences: List[War3SequenceProperties]):
def get_sequences(f2ms: float, mdl_sequences):
    sequences = []

    print("mdl_sequences: ", mdl_sequences)
    for sequence in mdl_sequences:
        print("mdl_sequence: ", sequence)
        sequences.append(War3AnimationSequence(sequence.name, sequence.start * f2ms, sequence.end * f2ms, sequence.non_looping, sequence.move_speed, sequence.rarity))

    if len(sequences) == 0:
        sequences.append(War3AnimationSequence("Stand", 0, 3333))

    sequences.sort(key=lambda x: x.start)

    return sequences
