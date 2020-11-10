def save_global_sequences(fw, model):
    # global_seqs = sorted(model.global_seqs)
    if len(model.global_seqs):
        fw("GlobalSequences %d {\n" % len(model.global_seqs))
        for sequence in model.global_seqs:
            fw("\tDuration %d,\n" % sequence)
        fw("}\n")
