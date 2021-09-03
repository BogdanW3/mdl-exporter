from typing import TextIO

from .write_mdl import write_mdl
from ..classes.War3Model import War3Model


def save_event_objects(fw: TextIO.write, model: War3Model):
    for event in model.objects['eventobject']:
        fw("EventObject \"%s\" {\n" % event.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[event.name])
        if event.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[event.parent])

        event_track = event.track
        if event_track is not None:
            write_mdl(event_track.keyframes, event_track.type,
                      event_track.interpolation, event_track.global_sequence,
                      event_track.handles_left, event_track.handles_right,
                      "EventTrack", fw, model.global_seqs, "\t")

        fw("}\n")
