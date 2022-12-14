import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator


class WAR3_OT_add_anim_sequence(Operator):
    """Add a Warcraft 3 animation sequence using timeline markers"""
    bl_idname = "war_3.add_anim_sequence"
    bl_label = "Add Warcraft 2 Sequence"
    bl_options = {'REGISTER', 'INTERNAL'}

    seq_name: StringProperty(
        name="Name",
        default="Stand"
        )

    start: IntProperty(
        name="Start Frame",
        default=1
        )

    end: IntProperty(
        name="End Frame",
        default=100
        )

    rarity: IntProperty(
        name="Rarity",
        default=0
        )

    non_looping: BoolProperty(
        name="Non Looping",
        default=False
        )

    def invoke(self, context: bpy.types.Context, event):
        scene = context.window.scene
        for name in ["Stand", "Birth", "Death", "Decay", "Portrait"]:
            if name not in (s.seq_name for s in scene.war3_mdl_sequences.mdl_sequences):
                self.seq_name = name
                break

        if len(scene.war3_mdl_sequences.mdl_sequences):
            last = max([s.end for s in scene.war3_mdl_sequences.mdl_sequences])
            self.start = last + 10
            self.end = self.start + 100

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context: bpy.types.Context):
        print("context: ", context)
        layout = self.layout
        layout.prop(self, "seq_name")
        layout.prop(self, "start")
        layout.prop(self, "end")
        layout.prop(self, "rarity")
        layout.prop(self, "non_looping")

    def execute(self, context: bpy.types.Context):
        scene = context.window.scene
        war3_mdl_sequences = scene.war3_mdl_sequences
        sequences = war3_mdl_sequences.mdl_sequences

        if sequences is not None:
            scene.timeline_markers.new(self.seq_name, frame=self.start)
            scene.timeline_markers.new(self.seq_name, frame=self.end)

            s = sequences.add()
            s.name = self.seq_name
            s.seq_name = self.seq_name
            s.rarity = self.rarity
            s.non_looping = self.non_looping

            war3_mdl_sequences.mdl_sequence_index = len(sequences) - 1

        return {'FINISHED'}
