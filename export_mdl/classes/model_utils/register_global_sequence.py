def register_global_sequence(global_seqs, curve):
    if curve is not None and curve.global_sequence > 0:
        global_seqs.add(curve.global_sequence)
