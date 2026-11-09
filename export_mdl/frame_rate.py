# Warcraft 3 times are whole milliseconds; Blender keys sit on frames. A frame rate is exact for a set of times
# when every time lands on a whole frame that exports back to the same millisecond.
from typing import Iterable, Optional, Set, Tuple

import bpy

from .action_compat import get_fcurves

# Tried first, in this order, so the result is a rate people know (Blizzard's SD models were made at 30)
COMMON_RATES = (30, 24, 25, 60, 50, 48, 100, 120, 240, 250, 500, 1000)
MIN_RATE = 24
MAX_RATE = 1000


def scene_fps(scene: Optional[bpy.types.Scene] = None) -> float:
    scene = scene or bpy.context.scene
    return scene.render.fps / scene.render.fps_base


def frame_to_ms(frame: float, fps: float) -> int:
    # The same rounding the exporter uses
    return int(round(frame * (1000 / fps)))


def ms_to_frame(time: float, fps: float) -> int:
    return int(round(time * fps / 1000))


def timing_error(times: Iterable[int], fps: float) -> int:
    """How far, in ms, the worst of these times moves when snapped to a frame at this rate."""
    return max((abs(frame_to_ms(ms_to_frame(t, fps), fps) - t) for t in times), default=0)


def is_exact(times: Iterable[int], fps: float) -> bool:
    return all(frame_to_ms(ms_to_frame(t, fps), fps) == t for t in times)


def exact_rate(times: Iterable[int]) -> int:
    """The rate to use for these times: the first common rate that's exact, else the lowest exact one."""
    times = set(int(round(t)) for t in times)
    for rate in COMMON_RATES:
        if is_exact(times, rate):
            return rate
    for rate in range(MIN_RATE, MAX_RATE + 1):
        if is_exact(times, rate):
            return rate
    return MAX_RATE


# ---- Times in a parsed model --------------------------------------------------------------------------------

def model_times(model) -> Set[int]:
    """Every time the import puts a key or marker at: sequence bounds, global sequence lengths, track keys inside
    a sequence (the game never reads the others) and event times."""
    sequences = [(s.start, s.end) for s in model.sequences]
    durations = list(getattr(model, 'global_sequence_durations', None) or [])
    times: Set[int] = set()
    for start, end in sequences:
        times.add(start)
        times.add(end)
    times.update(durations)

    def in_sequence(t):
        return any(start <= t <= end for start, end in sequences)

    def add_track(keys, global_sequence):
        looping = isinstance(global_sequence, int) and 0 <= global_sequence < len(durations)
        times.update(t for t in keys if looping or in_sequence(t))

    package = __name__.split('.')[0]
    seen = set()

    def walk(value):
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                walk(item)
        elif type(value).__module__.split('.')[0] == package and hasattr(value, '__dict__'):
            keyframes = getattr(value, 'keyframes', None)
            if isinstance(keyframes, dict) and hasattr(value, 'global_sequence'):
                add_track(keyframes, value.global_sequence)
                return
            event_times = getattr(value, 'event_times', None)
            if event_times:
                add_track(event_times, getattr(value, 'event_global_sequence', -1))
            for item in vars(value).values():
                walk(item)

    walk(model)
    return {int(round(t)) for t in times}


# ---- Times in the scene -------------------------------------------------------------------------------------

def _all_fcurves():
    for action in bpy.data.actions:
        yield from get_fcurves(action)


def scene_times(scene: bpy.types.Scene) -> Set[int]:
    """Keys (of every action) and timeline markers, in ms at the scene's current rate."""
    fps = scene_fps(scene)
    times = {frame_to_ms(m.frame, fps) for m in scene.timeline_markers}
    for fcurve in _all_fcurves():
        times.update(frame_to_ms(point.co[0], fps) for point in fcurve.keyframe_points)
    return times


def has_animation(scene: bpy.types.Scene) -> bool:
    return bool(len(scene.timeline_markers)) or any(len(fc.keyframe_points) for fc in _all_fcurves())


def change_frame_rate(scene: bpy.types.Scene, fps: int) -> Tuple[int, int]:
    """Set the scene's rate and move keys, handles, markers and frame ranges so they keep their time in ms (each
    snapped to a whole frame). Returns (keys moved, keys merged because they landed on the same frame)."""
    old = scene_fps(scene)
    if abs(old - fps) < 1e-9 and scene.render.fps_base == 1.0:
        return 0, 0
    ratio = fps / old

    def remap(frame):
        return ms_to_frame(frame_to_ms(frame, old), fps)

    moved = merged = 0
    for fcurve in _all_fcurves():
        frames = set()
        doomed = []
        for point in fcurve.keyframe_points:
            x = point.co[0]
            new_x = remap(x)
            if new_x in frames:
                doomed.append(point)
                continue
            frames.add(new_x)
            for handle in (point.handle_left, point.handle_right):
                handle[0] = new_x + (handle[0] - x) * ratio
            point.co[0] = new_x
            moved += 1
        for point in reversed(doomed):
            fcurve.keyframe_points.remove(point)
            merged += 1
        for modifier in fcurve.modifiers:
            if getattr(modifier, 'use_restricted_range', False):
                modifier.frame_start = remap(modifier.frame_start)
                modifier.frame_end = remap(modifier.frame_end)
        fcurve.update()

    window_manager = bpy.context.window_manager
    refreshing = getattr(window_manager, 'mdl_sequence_refreshing', False)
    if hasattr(window_manager, 'mdl_sequence_refreshing'):
        window_manager.mdl_sequence_refreshing = True  # Markers move, they aren't renamed or added
    try:
        for marker in scene.timeline_markers:
            marker.frame = remap(marker.frame)
    finally:
        if hasattr(window_manager, 'mdl_sequence_refreshing'):
            window_manager.mdl_sequence_refreshing = refreshing

    # Sequence lengths kept on armatures (the "use actions" mode)
    for obj in scene.objects:
        if obj.type == 'ARMATURE':
            for item in getattr(getattr(obj.data, 'war_3', None), 'sequencesList', ()):
                item['length'] = remap(item.length)

    end = remap(scene.frame_end)
    scene.frame_start = remap(scene.frame_start)
    scene.frame_end = max(end, scene.frame_start)
    if scene.use_preview_range:
        preview_end = remap(scene.frame_preview_end)
        scene.frame_preview_start = remap(scene.frame_preview_start)
        scene.frame_preview_end = max(preview_end, scene.frame_preview_start)
    current = remap(scene.frame_current)
    scene.render.fps = fps
    scene.render.fps_base = 1.0
    scene.frame_set(current)
    return moved, merged


def fit_scene_to(scene: bpy.types.Scene, times: Iterable[int]) -> Optional[int]:
    """Before an import: make sure these times (and what the scene already holds) land on whole frames. Keeps the
    scene's rate when it already works; otherwise changes it, moving the existing animation along. Returns the
    new rate, or None when nothing changed."""
    times = set(times)
    existing = scene_times(scene) if has_animation(scene) else set()
    fps = scene_fps(scene)
    if scene.render.fps_base == 1.0 and is_exact(times | existing, fps):
        return None
    rate = exact_rate(times | existing)
    change_frame_rate(scene, rate)
    return rate
