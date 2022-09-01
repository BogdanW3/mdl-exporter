from typing import List

import bpy
from ..War3AnimationAction import War3AnimationAction


def get_actions(f2ms: float, bpy_actions: List[bpy.types.Action]) -> List[War3AnimationAction]:
    actions = []

    for action in bpy_actions:
        if action.name != "all sequences":
            sequence = War3AnimationAction(action.name, action.frame_range[0] * f2ms,
                                           action.frame_range[1] * f2ms, False, 270)
            actions.append(sequence)

    if len(actions) == 0:
        actions.append(War3AnimationAction("Stand", 0, 1000))

    actions.sort(key=lambda x: x.start)

    return actions
