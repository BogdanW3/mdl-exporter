import bpy
from ..War3AnimationAction import War3AnimationAction


def get_actions(f2ms):
    actions = []

    for action in bpy.data.actions:
        if action.name != "all sequences":
            actions.append(War3AnimationAction(action.name, action.frame_range[0] * f2ms, action.frame_range[1] * f2ms, False, 270))

    if len(actions) == 0:
        actions.append(War3AnimationAction("Stand", 0, 3333))

    actions.sort(key=lambda x: x.start)

    return actions
