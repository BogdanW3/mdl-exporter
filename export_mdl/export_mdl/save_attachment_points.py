from .write_billboard import write_billboard
from .write_animations import write_animations


def save_attachment_points(fw, model):
    if len(model.objects['attachment']):
        for i, attachment in enumerate(model.objects['attachment']):
            fw("Attachment \"%s\" {\n" % attachment.name)

            if len(model.object_indices) > 1:
                fw("\tObjectId %d,\n" % model.object_indices[attachment.name])

            if attachment.parent is not None:
                fw("\tParent %d,\n" % model.object_indices[attachment.parent])

            write_billboard(fw, attachment.billboarded, attachment.billboard_lock)

            fw("\tAttachmentID %d,\n" % i)

            visibility = attachment.visibility
            if visibility is not None:
                write_animations(visibility.keyframes, visibility.type,
                                 visibility.interpolation, visibility.global_sequence,
                                 visibility.handles_left, visibility.handles_right,
                          "Visibility", fw, model.global_seqs, "\t")
                # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)
            fw("}\n")
