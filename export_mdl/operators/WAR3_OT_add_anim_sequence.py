import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator


class WAR3_OT_add_anim_sequence(Operator):
    """Add a Warcraft 3 animation sequence"""
    bl_idname = "war_3.add_anim_sequence"
    bl_label = "EE-Add Sequence"
    bl_options = {'REGISTER', 'INTERNAL'}

    name: StringProperty(
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
            if name not in (s.name for s in scene.mdl_sequences):
                self.name = name
                break

        if len(scene.mdl_sequences):
            last = max([s.end for s in scene.mdl_sequences])
            self.start = last + 10
            self.end = self.start + 100

        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context: bpy.types.Context):
        print("context: ", context)
        layout = self.layout
        layout.prop(self, "name")
        layout.prop(self, "start")
        layout.prop(self, "end")
        layout.prop(self, "rarity")
        layout.prop(self, "non_looping")

    def execute(self, context: bpy.types.Context):
        scene = context.window.scene
        sequences = scene.mdl_sequences

        scene.timeline_markers.new(self.name, frame=self.start)
        scene.timeline_markers.new(self.name, frame=self.end)

        s = sequences.add()
        s.name = self.name
        s.rarity = self.rarity
        s.non_looping = self.non_looping

        scene.mdl_sequence_index = len(sequences) - 1

        return {'FINISHED'}
