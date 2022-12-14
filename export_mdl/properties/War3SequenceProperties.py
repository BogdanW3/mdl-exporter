import bpy


def set_sequence_name(self, value):
    for marker in bpy.context.scene.timeline_markers:
        if marker.name == self.seq_name:
            marker.name = value
    self.seq_name = value
    self.name = value


def set_current_sequence(self):
    bpy.context.scene.frame_start = self.start
    bpy.context.scene.frame_end = self.end


def get_sequence_name(self):
    return self.seq_name


def get_sequence_start(self):
    scene = bpy.context.scene
    if not len(scene.war3_mdl_sequences.mdl_sequences):
        return 0
    # active_sequence = scene.mdl_sequences[scene.mdl_sequence_index]
    return min(tuple(m.frame for m in scene.timeline_markers if m.name == self.seq_name))


def get_sequence_end(self):
    scene = bpy.context.scene
    if not len(scene.war3_mdl_sequences.mdl_sequences):
        return 0
    # active_sequence = scene.mdl_sequences[scene.mdl_sequence_index]
    return max(tuple(m.frame for m in scene.timeline_markers if m.name == self.seq_name))


class War3SequenceProperties(bpy.types.PropertyGroup):

    # Backing field

    name_display: bpy.props.StringProperty(
        name="Name",
        default="Stand",
        get=get_sequence_name,
        set=set_sequence_name
        )

    seq_name: bpy.props.StringProperty(
        name="",
        default="Sequence"
        )

    start: bpy.props.IntProperty(
        name="",
        get=get_sequence_start
        )

    end: bpy.props.IntProperty(
        name="",
        get=get_sequence_end
        )

    rarity: bpy.props.IntProperty(
        name="Rarity",
        description="How rarely this sequence should play.",
        default=0,
        min=0
        )

    non_looping: bpy.props.BoolProperty(
        name="Non Looping",
        default=False
        )

    move_speed: bpy.props.IntProperty(
        name="Movement Speed",
        description="The unit movement speed at which this animation will play at 100% speed.",
        default=270,
        min=0
        )

