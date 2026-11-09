from typing import TextIO


def write_billboard(fw: TextIO.write, billboarded, billboard_lock, node_flags: int = 0):
    inherit = [name for bit, name in ((0x1, "Translation"), (0x2, "Rotation"), (0x4, "Scaling")) if node_flags & bit]
    if inherit:
        fw("\tDontInherit { %s },\n" % ", ".join(inherit))
    if node_flags & 0x80:
        fw("\tCameraAnchored,\n")
    for flag, axis in zip(billboard_lock, ('Z', 'Y', 'X')):
        if flag:
            fw("\tBillboardedLock%s,\n" % axis)
    if billboarded:
        fw("\tBillboarded,\n")
