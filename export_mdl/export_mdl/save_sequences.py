from export_mdl.utils import f2s, calc_bounds_radius


def save_sequences(fw, model):
    fw("Sequences %d {\n" % len(model.sequences))
    for sequence in model.sequences:
        fw("\tAnim \"%s\" {\n" % sequence.name)
        fw("\t\tInterval {%d, %d},\n" % (sequence.start, sequence.end))
        if sequence.non_looping:
            fw("\t\tNonLooping,\n")
        if 'walk' in sequence.name.lower():
            fw("\t\tMoveSpeed %d,\n" % sequence.movement_speed)

        fw("\t\tMinimumExtent {%s, %s, %s},\n" % tuple(map(f2s, model.global_extents_min)))
        fw("\t\tMaximumExtent {%s, %s, %s},\n" % tuple(map(f2s, model.global_extents_max)))
        fw("\t\tBoundsRadius %s,\n" % f2s(calc_bounds_radius(model.global_extents_min, model.global_extents_max)))
        fw("\t}\n")
    fw("}\n")