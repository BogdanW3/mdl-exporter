import math

import bpy
from mathutils import Euler

from .utils.split_segment import split_segment


class War3AnimationCurve:
    def __init__(self, fcurves, data_path, sequences, scale=1):
        frames = set()

        self.interpolation = 'Linear'
        self.global_sequence = -1
        self.type = 'Default'

        self.set_type(data_path)

        f2ms = 1000 / bpy.context.scene.render.fps

        self.parse_fcurve_values(f2ms, fcurves, frames, sequences)

        self.add_start_and_end_frames(f2ms, frames, sequences)

        self.keyframes = {}
        self.handles_right = {}
        self.handles_left = {}
        self.curves = []

        for frame in frames:
            values = []
            handle_left = []
            handle_right = []

            values, handle_left, handle_right = self.interpret_fcurves(data_path, fcurves, frame, scale)

            self.rotation_is_quaternation(data_path, frame, values)

            self.set_handles(data_path, frame, handle_left, handle_right)

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

    def set_handles(self, data_path, frame, handle_left, handle_right):
        if self.interpolation == 'Bezier':
            if 'rotation' in data_path and 'quaternion' not in data_path:
                self.handles_left[frame] = tuple(Euler(math.radians(x) for x in handle_left).to_quaternion())
                self.handles_right[frame] = tuple(Euler(math.radians(x) for x in handle_right).to_quaternion())
            else:
                self.handles_left[frame] = tuple(handle_right)
                self.handles_right[frame] = tuple(handle_right)

    def rotation_is_quaternation(self, data_path, frame, values):
        if 'rotation' in data_path and 'quaternion' not in data_path:  # Warcraft 3 only uses quaternions!
            self.keyframes[frame] = tuple(Euler(values).to_quaternion())
        else:
            self.keyframes[frame] = tuple(values)

    def interpret_fcurves(self, data_path, fcurves, frame, scale):
        values = []
        handle_left = []
        handle_right = []
        keys = fcurves.keys()
        keys = sorted(keys, key=lambda x: x[1])
        for key in keys:
            self.curves.append(fcurves[key])
            value = fcurves[key].evaluate(frame)
            values.append(value * scale)

            if 'color' in data_path:
                values = values[::-1]  # Colors are stored in reverse

            if 'hide_render' in data_path:
                values = [1 - v for v in values]  # Hide_Render is the opposite of visibility!

            if self.interpolation == 'Bezier':
                h_left = fcurves[key].evaluate(frame - 1)
                h_right = fcurves[key].evaluate(frame + 1)
                handle_left.append(h_left)
                handle_right.append(h_right)
        return values, handle_left, handle_right

    def add_start_and_end_frames(self, f2ms, frames, sequences):
        # We want start and end keyframes for each sequence. Make sure not to do this for events and global sequences, though!
        if self.global_sequence < 0 and self.type in {'Rotation', 'Translation', 'Scale'}:
            for sequence in sequences:
                frames.add(round(sequence.start / f2ms))
                frames.add(round(sequence.end / f2ms))

    def set_type(self, data_path):
        if 'rotation' in data_path:
            self.type = 'Rotation'
        elif 'location' in data_path:
            self.type = 'Translation'
        elif 'scale' in data_path:
            self.type = 'Scale'
        elif 'color' in data_path or 'default_value' in data_path:
            self.type = 'Color'
        elif 'event' in data_path.lower():
            self.type = 'Event'
        elif 'visibility' in data_path.lower() or 'hide_render' in data_path.lower():
            self.type = 'Boolean'

        if self.type == 'Boolean' or self.type == 'Event':
            self.interpolation = 'DontInterp'

    def parse_fcurve_values(self, f2ms, fcurves, frames, sequences):
        for fcurve in fcurves.values():
            if len(fcurve.keyframe_points):
                if fcurve.keyframe_points[0].interpolation == 'BEZIER' and self.type != 'Rotation':
                    # Nonlinear interpolation for rotations is disabled for now
                    self.interpolation = 'Bezier'
                elif fcurve.keyframe_points[0].interpolation == 'CONSTANT':
                    self.interpolation = 'DontInterp'

            for mod in fcurve.modifiers:
                if mod.type == 'CYCLES':
                    self.global_sequence = max(self.global_sequence, int(fcurve.range()[1] * f2ms))

            for keyframe in fcurve.keyframe_points:
                frame = keyframe.co[0] * f2ms
                for sequence in sequences:
                    if (frame >= sequence.start and frame <= sequence.end) or self.global_sequence > 0:
                        frames.add(keyframe.co[0])
                        break

    def optimize(self, tolerance, sequences):

        f2ms = 1000 / bpy.context.scene.render.fps

        if self.interpolation == 'Bezier':
            self.interpolation = 'Linear'  # This feature doesn't support bezier as of right now

        print('Before: %d' % len(self.keyframes))

        new_keys = []
        for sequence in sequences:
            start = int(round(sequence.start / f2ms))
            end = int(round(sequence.end / f2ms))
            new_keys += [(start, self.keyframes[start]), (end, self.keyframes[end])]
            new_keys += split_segment(self.keyframes, self.type, (start, self.keyframes[start]),
                                     (end, self.keyframes[end]), tolerance)

        self.keyframes.clear()
        self.keyframes.update(new_keys)
        print('After: %d' % len(self.keyframes))

    def get_wc3_animation_curve(anim_data, data_path, num_indices, sequences, scale=1):
        curves = {}

        if anim_data and anim_data.action:
            for index in range(num_indices):
                curve = anim_data.action.fcurves.find(data_path, index=index)
                if curve is not None:
                    curves[(data_path.split('.')[-1], index)] = curve
                    # For now, i'm just interested in the type, not the whole data path. Hence, the split returns the name after the last dot.

        if len(curves):
            return War3AnimationCurve(curves, data_path, sequences, scale)
        return None
