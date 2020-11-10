from ..War3AnimationSequence import War3AnimationSequence


def get_sequences(f2ms, scene):
    sequences = []

    for sequence in scene.mdl_sequences:
        sequences.append(War3AnimationSequence(sequence.name, sequence.start * f2ms, sequence.end * f2ms, sequence.non_looping, sequence.move_speed))

    if len(sequences) == 0:
        sequences.append(War3AnimationSequence("Stand", 0, 3333))

    sequences.sort(key=lambda x:x.start)

    return sequences
