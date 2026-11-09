import bpy

from ..geoset_preview import add_geoset_preview


class WAR3_OT_geoset_preview(bpy.types.Operator):
    bl_idname = 'war_3.geoset_preview'
    bl_label = 'Preview in Viewport'
    bl_description = ("Show the geoset alpha and color in Material Preview: drives the object's color from them "
                      "and multiplies Object Info into its materials. Doesn't change what's exported")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return any(obj.type == 'MESH' for obj in context.selected_objects) or \
            (context.active_object is not None and context.active_object.type == 'MESH')

    def execute(self, context: bpy.types.Context):
        objects = {obj for obj in context.selected_objects if obj.type == 'MESH'}
        if context.active_object is not None and context.active_object.type == 'MESH':
            objects.add(context.active_object)
        for obj in objects:
            add_geoset_preview(obj)
        self.report({'INFO'}, "Geoset preview on %d object(s)" % len(objects))
        return {'FINISHED'}
