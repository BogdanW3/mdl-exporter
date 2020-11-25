def space_actions(action_list):
    last_action_frame = 0
    action_spacing = 10
    for action in action_list:
        action.start = action.start + last_action_frame + action_spacing
        action.end = action.end + last_action_frame + action_spacing
        last_action_frame = action.end
