from typing import List

from export_mdl.classes.War3AnimationAction import War3AnimationAction


def space_actions(sequence_list: List[War3AnimationAction]):
    last_action_frame = 0
    action_spacing = 10
    for action in sequence_list:
        action.start = action.start + last_action_frame + action_spacing
        action.end = action.end + last_action_frame + action_spacing
        last_action_frame = action.end
