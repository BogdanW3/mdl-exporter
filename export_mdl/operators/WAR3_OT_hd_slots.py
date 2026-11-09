import bpy

from ..hd_slots import HD_SLOT_NAMES, fill_hd_slots, node_paths, set_slot


class WAR3_OT_hd_slots(bpy.types.Operator):
    bl_idname = 'war_3.hd_slots'
    bl_label = 'HD Texture Slots'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    action: bpy.props.EnumProperty(items=[
        ('FILL', "Fill Texture Slots", "Add the texture slots this HD material is missing, from the node tree's "
                                       "images or the game's default textures"),
        ('DEFAULT', "Use Default", "Point this slot back at the game's default texture"),
        ('NODES', "From Node Tree", "Take this slot's texture from the image the node tree uses for it"),
    ])

    @classmethod
    def description(cls, context, properties):
        return {'FILL': "Add the texture slots this HD material is missing, from the node tree's images or the "
                        "game's default textures",
                'DEFAULT': "Point this slot back at the game's default texture",
                'NODES': "Take this slot's texture from the image the node tree uses for it"}[properties.action]

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.active_material is not None

    def execute(self, context):
        material = context.active_object.active_material
        if self.action == 'FILL':
            added = fill_hd_slots(material)
            self.report({'INFO'}, "Added %d texture slots" % added)
            return {'FINISHED'}
        index = material.mdl_layer_index
        if not 0 <= index < min(len(material.mdl_layers), len(HD_SLOT_NAMES)):
            return {'CANCELLED'}
        item = material.mdl_layers[index]
        if self.action == 'DEFAULT':
            set_slot(item, index)
        else:
            path = node_paths(material)[index]
            if path is None:
                self.report({'WARNING'}, "The node tree has no image for the %s slot" % HD_SLOT_NAMES[index])
                return {'CANCELLED'}
            set_slot(item, index, path)
        return {'FINISHED'}
