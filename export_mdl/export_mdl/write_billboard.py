def write_billboard(fw, billboarded, billboard_lock):
    for flag, axis in zip(billboard_lock, ('Z', 'Y', 'X')):
        if flag:
            fw("\tBillboardedLock%s,\n" % axis)
    if billboarded:
        fw("\tBillboarded,\n")
