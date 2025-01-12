from bpy.props import EnumProperty
from bpy.types import Operator


class WAR3_OT_material_list_action(Operator):
    # """Move items up and down, add and remove"""
    bl_idname = "war_3.list_action"
    bl_label = ""
    # bl_label = "Material List Actions"
    # bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER', 'INTERNAL'}

    name_counter = 0

    action_dict = {
        'UP': ('UP', "Up", "Move layer up"),
        'DOWN': ('DOWN', "Down", "Move layer down"),
        'REMOVE': ('REMOVE', "Remove", "Remove layer"),
        'ADD': ('ADD', "Add", "Add layer")
    }
    action: EnumProperty(
        items=action_dict.values())

    @classmethod
    def description(cls, context, properties: 'WAR3_OT_material_list_action'):
        return cls.action_dict[properties.action][2]

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.active_material is not None

    def invoke(self, context, event):
        try:
            mat = context.active_object.active_material
            i = mat.mdl_layer_index
            item = mat.mdl_layers[i]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and i < len(mat.mdl_layers) - 1:
                mat.mdl_layers.move(i, i+1)
                mat.mdl_layer_index += 1
            elif self.action == 'UP' and i >= 1:
                mat.mdl_layers.move(i, i-1)
                mat.mdl_layer_index -= 1

            elif self.action == 'REMOVE':
                if i > 0:
                    mat.mdl_layer_index -= 1
                if len(mat.mdl_layers):
                    mat.mdl_layers.remove(i)

        if self.action == 'ADD':
            if context.active_object:
                item = mat.mdl_layers.add()
                item.name = "Layer %d" % self.name_counter
                WAR3_OT_material_list_action.name_counter += 1
                mat.mdl_layer_index = len(mat.mdl_layers)-1
            else:
                self.report({'INFO'}, "Nothing selected in the Viewport")

        return {"FINISHED"}
