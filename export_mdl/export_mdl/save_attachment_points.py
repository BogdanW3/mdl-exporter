from typing import TextIO, Set, List

from .write_billboard import write_billboard
from .write_animation_chunk import write_animation_chunk
from ..classes.War3Attachment import War3Attachment


def save_attachment_points(fw: TextIO.write, attachments: List[War3Attachment], global_seqs: Set[int]):
    if len(attachments):
        for i, attachment in enumerate(attachments):
            fw("Attachment \"%s\" {\n" % attachment.name)

            if 0 <= attachment.obj_id:
                fw("\tObjectId %d,\n" % attachment.obj_id)

            if attachment.parent_id is not None:
                fw("\tParent %d,\n" % attachment.parent_id)

            write_billboard(fw, attachment.billboarded, attachment.billboard_lock)

            fw("\tAttachmentID %d,\n" % i)

            visibility = attachment.visibility
            if visibility is not None:
                write_animation_chunk(fw, visibility, "Visibility", global_seqs, "\t")
                # write_animation_chunk(visibility.keyframes, visibility.type,
                #                       visibility.interpolation, visibility.global_sequence,
                #                       visibility.handles_left, visibility.handles_right,
                #           "Visibility", fw, global_seqs, "\t")
            fw("}\n")
