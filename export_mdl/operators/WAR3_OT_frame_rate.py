import bpy

from ..frame_rate import scene_times, exact_rate, timing_error, change_frame_rate, scene_fps


class WAR3_OT_set_frame_rate(bpy.types.Operator):
    bl_idname = 'war_3.set_frame_rate'
    bl_label = 'Change Frame Rate'
    bl_description = ("Change the scene's frame rate and move every key, marker and frame range along so it keeps "
                      "its timing in milliseconds. Suggests the lowest rate where every key lands on a whole frame")
    bl_options = {'REGISTER', 'UNDO'}

    fps: bpy.props.IntProperty(name='Frame Rate', min=1, max=1000, default=30)

    _times = set()
    _suggested = 30

    def invoke(self, context, event):
        cls = type(self)
        cls._times = scene_times(context.scene)
        cls._suggested = exact_rate(cls._times)
        self.fps = cls._suggested
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        cls = type(self)
        current = scene_fps(context.scene)
        error = timing_error(cls._times, current)
        col = layout.column(align=True)
        col.label(text="Now %g fps%s" % (current, ", keys are off by up to %d ms" % error if error else ""))
        col.label(text="Every key lands on a whole frame at %d fps" % cls._suggested)
        layout.prop(self, 'fps')
        if self.fps != round(current):
            error = timing_error(cls._times, self.fps)
            if error:
                layout.label(text="Keys between frames move by up to %d ms" % error, icon='ERROR')
            else:
                layout.label(text="Every key keeps its exact timing", icon='CHECKMARK')

    def execute(self, context):
        error = timing_error(scene_times(context.scene), self.fps)
        moved, merged = change_frame_rate(context.scene, self.fps)
        message = "Frame rate is now %d fps" % self.fps
        if merged:
            message += "; %d keys landed on a frame that already had one and were dropped" % merged
        elif error:
            message += "; keys moved by up to %d ms" % error
        self.report({'WARNING'} if merged else {'INFO'}, message)
        return {'FINISHED'}
