import math

import bpy
from mathutils import Euler
from typing import Union, Tuple, Dict, Set, List

from .War3AnimationAction import War3AnimationAction
from .animation_curve_utils.split_segment import split_segment


class War3AnimationCurve:
    def __init__(self):
        self.interpolation = 'Linear'
        self.global_sequence: int = -1
        self.type = 'Default'

        self.keyframes: Dict[float, List[float]] = {}
        self.handles_right: Dict[float, List[float]] = {}
        self.handles_left: Dict[float, List[float]] = {}
        self.curves: List[bpy.types.FCurve] = []
        # self.keyframes: Dict[float, tuple] = {}
        # self.handles_right: Dict[float, tuple] = {}
        # self.handles_left: Dict[float, tuple] = {}
        # self.curves: List[bpy.types.FCurve] = []

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            if self.interpolation != other.interpolation:
                return False
            if self.global_sequence != other.global_sequence:
                return False
            if len(self.keyframes) != len(other.keyframes):
                return False

            return self.keyframes == other.keyframes and self.handles_left == other.handles_left and self.handles_right == other.handles_right

        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        values = [self.interpolation, self.global_sequence, self.type]
        values.append(tuple(sorted(self.keyframes.items())))
        values.append(tuple(sorted(self.handles_left.items())))
        values.append(tuple(sorted(self.handles_right.items())))
        return hash(tuple(values))

# import math
#
# import bpy
# from mathutils import Euler
# from typing import Union, Tuple, Dict, Set, List
#
# from .War3AnimationAction import War3AnimationAction
# from .animation_curve_utils.split_segment import split_segment
#
#
# class War3AnimationCurve:
#     def __init__(self,
#                  fcurves: Dict[Tuple[str, int], Union[int, bpy.types.FCurve]],
#                  data_path: str,
#                  sequences: List[War3AnimationAction],
#                  scale=1):
#         frames: Set[float] = set()
#
#         self.interpolation = 'Linear'
#         self.global_sequence: int = -1
#         self.type = 'Default'
#
#         self.set_type(data_path)
#
#         f2ms = 1000 / bpy.context.scene.render.fps
#
#         self.parse_fcurve_values(f2ms, fcurves, frames, sequences)
#
#         if len(frames) <= 1:
#             self.interpolation = 'Linear'
#
#         self.add_start_and_end_frames(f2ms, frames, sequences)
#
#         self.keyframes: Dict[float, tuple] = {}
#         self.handles_right: Dict[float, tuple] = {}
#         self.handles_left: Dict[float, tuple] = {}
#         self.curves: List[int, bpy.types.FCurve] = []
#
#         for frame in frames:
#             values: List[float]
#             handle_left: List[float]
#             handle_right: List[float]
#
#             values, handle_left, handle_right = self.interpret_fcurves(data_path, fcurves, frame, scale)
#
#             self.rotation_is_quaternation(data_path, frame, values)
#
#             self.set_handles(data_path, frame, handle_left, handle_right)
#
#     def __eq__(self, other):
#         if isinstance(self, other.__class__):
#             if self.interpolation != other.interpolation:
#                 return False
#             if self.global_sequence != other.global_sequence:
#                 return False
#             if len(self.keyframes) != len(other.keyframes):
#                 return False
#
#             return self.keyframes == other.keyframes and self.handles_left == other.handles_left and self.handles_right == other.handles_right
#
#         return NotImplemented
#
#     def __ne__(self, other):
#         return not self.__eq__(other)
#
#     def __hash__(self):
#         values = [self.interpolation, self.global_sequence, self.type]
#         values.append(tuple(sorted(self.keyframes.items())))
#         values.append(tuple(sorted(self.handles_left.items())))
#         values.append(tuple(sorted(self.handles_right.items())))
#         return hash(tuple(values))
#
#     def set_handles(self, data_path: str, frame: float, handle_left: List[float], handle_right: List[float]):
#         if self.interpolation == 'Bezier':
#             if 'rotation' in data_path and 'quaternion' not in data_path:
#                 self.handles_left[frame] = tuple(Euler(math.radians(v) for v in handle_left).to_quaternion())
#                 self.handles_right[frame] = tuple(Euler(math.radians(v) for v in handle_right).to_quaternion())
#             else:
#                 self.handles_left[frame] = tuple(handle_right)
#                 self.handles_right[frame] = tuple(handle_right)
#
#     def rotation_is_quaternation(self, data_path: str, frame: float, values: List[float]):
#         if 'rotation' in data_path and 'quaternion' not in data_path:  # Warcraft 3 only uses quaternions!
#             # euler = Euler(values)
#             # quaternion = euler.to_quaternion()
#             # self.keyframes[frame] = tuple([quaternion.x, quaternion.y, quaternion.z, quaternion.w])
#             self.keyframes[frame] = tuple(Euler(values).to_quaternion())
#         else:
#             self.keyframes[frame] = tuple(values)
#
#     def interpret_fcurves(self, data_path: str,
#                           fcurves: Dict[Tuple[str, int], Union[int, bpy.types.FCurve]],
#                           frame: float, scale: float) -> Tuple[List[float], List[float], List[float]]:
#         values: List[float] = []
#         handle_left: List[float] = []
#         handle_right: List[float] = []
#         # keys: KeysView = fcurves.keys()
#         keys: List[Tuple[str, int]] = sorted(fcurves.keys(), key=lambda x: x[1])
#         for key in keys:
#             self.curves.append(fcurves[key])
#             value = fcurves[key].evaluate(frame)
#             values.append(value * scale)
#
#             if 'color' in data_path:
#                 values = values[::-1]  # Colors are stored in reverse
#
#             if 'hide_render' in data_path:
#                 values = [1 - v for v in values]  # Hide_Render is the opposite of visibility!
#
#             if self.interpolation == 'Bezier':
#                 h_left = fcurves[key].evaluate(frame - 1)
#                 h_right = fcurves[key].evaluate(frame + 1)
#                 handle_left.append(h_left)
#                 handle_right.append(h_right)
#         return values, handle_left, handle_right
#
#     def add_start_and_end_frames(self, f2ms: float, frames: Set[float], sequences: List[War3AnimationAction]):
#         # We want start and end keyframes for each sequence.
#         # Make sure not to do this for events and global sequences, though!
#         if self.global_sequence < 0 and self.type in {'Rotation', 'Translation', 'Scale'}:
#             for sequence in sequences:
#                 frames.add(round(sequence.start / f2ms))
#                 frames.add(round(sequence.end / f2ms))
#
#     def set_type(self, data_path: str):
#         if 'rotation' in data_path:
#             self.type = 'Rotation'
#         elif 'location' in data_path:
#             self.type = 'Translation'
#         elif 'scale' in data_path:
#             self.type = 'Scale'
#         elif 'color' in data_path or 'default_value' in data_path:
#             self.type = 'Color'
#         elif 'event' in data_path.lower():
#             self.type = 'Event'
#         elif 'visibility' in data_path.lower() or 'hide_render' in data_path.lower():
#             self.type = 'Boolean'
#
#         if self.type == 'Boolean' or self.type == 'Event':
#             self.interpolation = 'DontInterp'
#
#     def parse_fcurve_values(self, f2ms: float, fcurves: Dict[Tuple[str, int], Union[int, bpy.types.FCurve]],
#                             frames: Set[float], sequences: List[War3AnimationAction]):
#         for fcurve in fcurves.values():
#             if len(fcurve.keyframe_points):
#                 if fcurve.keyframe_points[0].interpolation == 'BEZIER' and self.type != 'Rotation':
#                     # Nonlinear interpolation for rotations is disabled for now
#                     self.interpolation = 'Bezier'
#                 elif fcurve.keyframe_points[0].interpolation == 'CONSTANT':
#                     self.interpolation = 'DontInterp'
#
#             for mod in fcurve.modifiers:
#                 if mod.type == 'CYCLES':
#                     self.global_sequence = max(self.global_sequence, int(fcurve.range()[1] * f2ms))
#
#             for keyframe in fcurve.keyframe_points:
#                 frame: float = keyframe.co[0] * f2ms
#                 for sequence in sequences:
#                     if (sequence.start <= frame <= sequence.end) or self.global_sequence > 0:
#                         frames.add(keyframe.co[0])
#                         break
#
#     def optimize(self, tolerance: float, sequences: List[War3AnimationAction]):
#
#         f2ms = 1000 / bpy.context.scene.render.fps
#
#         if self.interpolation == 'Bezier':
#             self.interpolation = 'Linear'  # This feature doesn't support bezier as of right now
#
#         print('Before: %d' % len(self.keyframes))
#
#         new_keys = []
#         for sequence in sequences:
#             start = int(round(sequence.start / f2ms))
#             end = int(round(sequence.end / f2ms))
#             start_value = self.keyframes[start]
#             start_ = (start, self.keyframes[start])
#             end_ = (end, self.keyframes[end])
#             end_value = self.keyframes[end]
#             new_keys += [start_, end_]
#             # new_keys += split_segment(self.keyframes, self.type, start_, end_, tolerance)
#             new_keys += split_segment(self.keyframes, self.type, start, start_value, end, end_value, tolerance)
#
#         self.keyframes.clear()
#         self.keyframes.update(new_keys)
#         print('After: %d' % len(self.keyframes))
