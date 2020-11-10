import bpy

from ..utils import f2s, rnd


def write_mdl(keyframes, type1, interpolation, global_sequence, handles_left, handles_right, name, fw, global_seqs,
              indent="\t"):

    f2ms = 1000 / bpy.context.scene.render.fps

    fw(indent + "%s %d {\n" % (name, len(keyframes)))

    if type1 != 'Event':
        fw(indent + "\t%s,\n" % interpolation)
    if global_sequence > 0:
        fw(indent + "\tGlobalSeqId %d,\n" % global_seqs.index(global_sequence))

    for frame in sorted(keyframes.keys()):
        line = ""
        n = len(keyframes[frame])

        if n > 1:
            line += "{ "

        line += '%s, '*(n-1)
        line += '%s'

        if n > 1:
            line += ' },\n'
        else:
            line += ',\n'

        if type1 == 'Event':
            fw(indent+"\t%d,\n" % (frame * f2ms))
        else:
            keyframe = keyframes[frame]

            if type1 == 'Rotation':
                keyframe = keyframe[1:] + keyframe[:1]  # MDL quaternions must be on the form XYZW

            s = "\t%d: " % (frame * f2ms)
            fw(indent+s+line % tuple(f2s(rnd(x)) for x in keyframe))

            if interpolation == 'Bezier':
                hl = handles_left[frame]
                hr = handles_right[frame]

                if type1 == 'Rotation':
                    hl = hl[1:]+hl[:1]
                    hr = hr[1:]+hr[:1]

                fw(indent+"\t\tInTan "+line % tuple(f2s(rnd(x)) for x in hl))
                fw(indent+"\t\tOutTan "+line % tuple(f2s(rnd(x)) for x in hr))

    fw(indent+"}\n")
