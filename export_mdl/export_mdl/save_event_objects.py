from .write_mdl import write_mdl


def save_event_objects(fw, model):
    for event in model.objects['eventobject']:
        fw("EventObject \"%s\" {\n" % event.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[event.name])
        if event.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[event.parent])
        eventtrack = event.track
        if eventtrack is not None:
            write_mdl(eventtrack.keyframes, eventtrack.type, eventtrack.interpolation, eventtrack.global_sequence,
                      eventtrack.handles_left, eventtrack.handles_right, "EventTrack", fw, model.global_seqs, "\t")

        fw("}\n")
