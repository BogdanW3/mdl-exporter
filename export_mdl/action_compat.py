# Helpers that hide the difference between legacy actions (one flat F-Curve list, Blender < 4.4)
# and slotted/layered actions (Blender 4.4+, the only kind left in 5.0+, where Action.fcurves is gone).
from typing import Iterator, List, Optional

import bpy


def is_layered(action: bpy.types.Action) -> bool:
    return not hasattr(action, "fcurves")


def iter_channelbags(action: bpy.types.Action) -> Iterator:
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in getattr(strip, "channelbags", ()):
                yield channelbag


def get_fcurves(action: Optional[bpy.types.Action]) -> List[bpy.types.FCurve]:
    if action is None:
        return []
    if not is_layered(action):
        return list(action.fcurves)
    fcurves: List[bpy.types.FCurve] = []
    for channelbag in iter_channelbags(action):
        fcurves.extend(channelbag.fcurves)
    return fcurves


def find_fcurve(action: Optional[bpy.types.Action], data_path: str, index: int = 0) -> Optional[bpy.types.FCurve]:
    if action is None:
        return None
    if not is_layered(action):
        return action.fcurves.find(data_path, index=index)
    for channelbag in iter_channelbags(action):
        fcurve = channelbag.fcurves.find(data_path, index=index)
        if fcurve is not None:
            return fcurve
    return None


def ensure_channelbag(action: bpy.types.Action, id_type: str = 'OBJECT'):
    slot = next((s for s in action.slots if s.target_id_type in (id_type, 'UNSPECIFIED')), None)
    if slot is None:
        slot = action.slots.new(id_type=id_type, name=action.name)
    if len(action.layers):
        layer = action.layers[0]
    else:
        layer = action.layers.new("Layer")
    if len(layer.strips):
        strip = layer.strips[0]
    else:
        strip = layer.strips.new(type='KEYFRAME')
    return strip.channelbag(slot, ensure=True)


def new_fcurve(action: bpy.types.Action, data_path: str, index: int = 0,
               group_name: str = "", id_type: str = 'OBJECT') -> bpy.types.FCurve:
    if not is_layered(action):
        if group_name:
            return action.fcurves.new(data_path, index=index, action_group=group_name)
        return action.fcurves.new(data_path, index=index)
    channelbag = ensure_channelbag(action, id_type)
    return channelbag.fcurves.new(data_path, index=index, group_name=group_name)


def ensure_fcurve(action: bpy.types.Action, data_path: str, index: int = 0,
                  group_name: str = "", id_type: str = 'OBJECT') -> bpy.types.FCurve:
    fcurve = find_fcurve(action, data_path, index)
    if fcurve is None:
        fcurve = new_fcurve(action, data_path, index, group_name, id_type)
    return fcurve


def assign_action(id_data: bpy.types.ID, action: Optional[bpy.types.Action]):
    """Assigns the action and, on Blender 4.4+, a slot - which Blender 5.x no longer picks on its own."""
    if id_data.animation_data is None:
        id_data.animation_data_create()
    anim_data = id_data.animation_data
    anim_data.action = action
    if action is None or not hasattr(anim_data, "action_slot") or anim_data.action_slot is not None:
        return
    suitable = list(anim_data.action_suitable_slots)
    if not suitable:
        id_type = getattr(id_data, "id_type", 'OBJECT')
        ensure_channelbag(action, id_type)
        suitable = list(anim_data.action_suitable_slots)
    if suitable:
        anim_data.action_slot = suitable[0]


def get_action_slot(id_data: bpy.types.ID):
    anim_data = id_data.animation_data
    if anim_data is None:
        return None
    return getattr(anim_data, "action_slot", None)


def restore_action(id_data: bpy.types.ID, action: Optional[bpy.types.Action], slot):
    anim_data = id_data.animation_data
    if anim_data is None:
        return
    anim_data.action = action
    if slot is not None and hasattr(anim_data, "action_slot"):
        try:
            anim_data.action_slot = slot
        except (TypeError, RuntimeError):
            pass
