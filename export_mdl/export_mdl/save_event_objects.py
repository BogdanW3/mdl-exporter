from typing import TextIO, Dict, Set, List

from .write_animation_chunk import write_animation_chunk
from ..classes.War3EventObject import War3EventObject


def save_event_objects(fw: TextIO.write,
                       event_objects: List[War3EventObject],
                       object_indices: Dict[str, int],
                       global_seqs: Set[int]):
    for event in event_objects:
        fw("EventObject \"%s\" {\n" % event.name)
        if len(object_indices) > 1:
            fw("\tObjectId %d,\n" % object_indices[event.name])
        if event.parent is not None:
            fw("\tParent %d,\n" % object_indices[event.parent])

        event_track = event.track
        if event_track is not None:
            write_animation_chunk(fw, event_track, "EventTrack", global_seqs, "\t")
            # write_animation_chunk(event_track.keyframes, event_track.type,
            #                       event_track.interpolation, event_track.global_sequence,
            #                       event_track.handles_left, event_track.handles_right,
            #           "EventTrack", fw, model.global_seqs, "\t")

        fw("}\n")
