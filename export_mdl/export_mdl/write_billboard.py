def write_billboard(fw, billboarded, billboard_lock):
    for flag, axis in zip(billboard_lock, ('Z', 'Y', 'X')):
        if flag == True:
            fw("\tBillboardedLock%s,\n" % axis)
    if billboarded == True:
        fw("\tBillboarded,\n")