from typing import TextIO, Tuple, Dict, Set, List

import bpy

from ..classes.War3AnimationCurve import War3AnimationCurve
from ..utils import float2str, rnd


# def write_animation_chunk(keyframes: Dict[float, tuple], type1: str, interpolation: str,
#                           global_sequence: int, handles_left: Dict[float, tuple], handles_right: Dict[float, tuple],
#                           name: str, fw: TextIO.write,
#                           global_seqs: Set[int], indent="\t"):
#
#     f2ms = 1000 / bpy.context.scene.render.fps
#
#     fw(indent + "%s %d {\n" % (name, len(keyframes)))
#
#     if type1 != 'Event':
#         fw(indent + "\t%s,\n" % interpolation)
#     if global_sequence > 0:
#         fw(indent + "\tGlobalSeqId %d,\n" % global_seqs.index(global_sequence))
#
#     for frame in sorted(keyframes.keys()):
#         line = ""
#         n = len(keyframes[frame])
#
#         if n > 1:
#             line += "{ "
#
#         line += '%s, '*(n-1)
#         line += '%s'
#
#         if n > 1:
#             line += ' },\n'
#         else:
#             line += ',\n'
#
#         if type1 == 'Event':
#             fw(indent+"\t%d,\n" % (frame * f2ms))
#         else:
#             keyframe = keyframes[frame]
#
#             if type1 == 'Rotation':
#                 keyframe = keyframe[1:] + keyframe[:1]  # MDL quaternions must be on the form XYZW
#
#             s = "\t%d: " % (frame * f2ms)
#             fw(indent + s + line % tuple(float2str(rnd(x)) for x in keyframe))
#
#             if interpolation == 'Bezier':
#                 hl = handles_left[frame]
#                 hr = handles_right[frame]
#
#                 if type1 == 'Rotation':
#                     hl = wxyz_to_xyzw(hl)
#                     hr = wxyz_to_xyzw(hr)
#
#                 fw(indent +"\t\tInTan " + line % tuple(float2str(rnd(x)) for x in hl))
#                 fw(indent +"\t\tOutTan " + line % tuple(float2str(rnd(x)) for x in hr))
#
#     fw(indent+"}\n")


def write_animation_chunk(fw: TextIO.write,
                          animation: War3AnimationCurve,
                          name: str,
                          global_seqs: Set[int],
                          indent="\t"):
    keyframes: Dict[float, tuple] = animation.keyframes
    type1: str = animation.type
    interpolation: str = animation.interpolation
    global_sequence: int = animation.global_sequence
    handles_left: Dict[float, tuple] = animation.handles_left
    handles_right: Dict[float, tuple] = animation.handles_right
    # name: str
    # global_seqs: Set[int]


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
            fw(indent + s + line % tuple(float2str(rnd(x)) for x in keyframe))

            if interpolation == 'Bezier':
                hl = handles_left[frame]
                hr = handles_right[frame]

                if type1 == 'Rotation':
                    hl = wxyz_to_xyzw(hl)
                    hr = wxyz_to_xyzw(hr)

                fw(indent +"\t\tInTan " + line % tuple(float2str(rnd(x)) for x in hl))
                fw(indent +"\t\tOutTan " + line % tuple(float2str(rnd(x)) for x in hr))

    fw(indent+"}\n")


def wxyz_to_xyzw(quat: Tuple[float]):
    ugg: float = quat[0]
    quat1: List[float] = []
    quat1.extend(quat[1:])
    quat1.extend(quat[:1])
    quat: Tuple[float] = tuple(quat1)
    return quat
