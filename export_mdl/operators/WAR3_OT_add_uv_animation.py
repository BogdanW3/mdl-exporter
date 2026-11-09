import bpy

from ..hd_slots import is_hd
from ..uv_animation import add_uv_animation


class WAR3_OT_add_uv_animation(bpy.types.Operator):
    bl_idname = 'war_3.add_uv_animation'
    bl_label = 'Add Texture Animation'
    bl_description = ("Add a Mapping node that moves this layer's UVs: key its Location, Rotation and Scale on the "
                      "scene timeline (Warcraft 3 UV space, V runs top to bottom)")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        mat = obj.active_material if obj is not None else None
        return mat is not None and 0 <= mat.mdl_layer_index < len(mat.mdl_layers)

    def execute(self, context):
        mat = context.active_object.active_material
        if not mat.use_nodes:
            mat.use_nodes = True
        index = mat.mdl_layer_index
        images = [n for n in mat.node_tree.nodes if n.bl_idname == 'ShaderNodeTexImage']
        # Imported materials say which image is whose; otherwise every image not already mapped
        tagged = [n for n in images if is_hd(mat) or n.get("mdl_layer") == index]
        targets = tagged or [n for n in images if not n.inputs['Vector'].is_linked]
        node = add_uv_animation(mat, targets, "UV Animation %d" % index)
        mat.mdl_layers[index].uv_node = node.name
        self.report({'INFO'}, "Key the Location, Rotation and Scale of %s" % node.name)
        return {'FINISHED'}
