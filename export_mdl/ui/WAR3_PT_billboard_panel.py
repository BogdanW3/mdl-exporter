import bpy
from bpy.props import PointerProperty, EnumProperty
from bpy.types import Panel

from ..properties import War3BillboardProperties


class WAR3_PT_billboard_panel(Panel):
    """Displays billboard settings in the Object panel"""
    bl_idname = "WAR3_PT_billboard_panel"
    bl_label = "Warcraft 3 Billboard"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'object'

    @classmethod
    def register(cls):
        bpy.types.Object.mdl_billboard = PointerProperty(type=War3BillboardProperties.War3BillboardProperties)
        bpy.types.Bone.mdl_billboard = PointerProperty(type=War3BillboardProperties.War3BillboardProperties)
        bpy.types.Bone.mdl_node_kind = EnumProperty(
            name="Export As",
            items=[('AUTO', "Automatic", "A bone, or a helper when \"Demote Bones To Helpers\" is on and no mesh "
                                         "uses it"),
                   ('BONE', "Bone", "Always a bone"),
                   ('HELPER', "Helper", "Always a helper: a node that only moves its children, never a mesh "
                                        "directly")],
            default='AUTO')

    @classmethod
    def unregister(cls):
        del bpy.types.Object.mdl_billboard
        del bpy.types.Bone.mdl_billboard
        del bpy.types.Bone.mdl_node_kind

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object

        if obj is None:
            return False

        if obj.type == 'EMPTY' and obj.name.lower().startswith("bone"):
            return True

        if obj.type in ('LAMP', 'LIGHT'):
            return True

        if obj.name.endswith(" Ref") or obj.get("mdl_node_type"):
            return True

        return False

    def draw(self, context):
        layout = self.layout
        data = bpy.context.active_object.mdl_billboard
        layout.prop(data, "billboarded")
        layout.prop(data, "billboard_lock_x")
        layout.prop(data, "billboard_lock_y")
        layout.prop(data, "billboard_lock_z")
        col = layout.column(heading="Node")
        for prop in ("camera_anchored", "dont_inherit_translation", "dont_inherit_rotation", "dont_inherit_scaling"):
            if hasattr(data, prop):
                col.prop(data, prop)


class WAR3_PT_bone_billboard_panel(Panel):
    """Billboard settings of the active bone"""
    bl_idname = "WAR3_PT_bone_billboard_panel"
    bl_label = "Warcraft 3 Bone"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return context.bone is not None and hasattr(context.bone, "mdl_billboard")

    def draw(self, context):
        layout = self.layout
        data = context.bone.mdl_billboard
        if hasattr(context.bone, "mdl_node_kind"):
            layout.prop(context.bone, "mdl_node_kind")
        layout.prop(data, "billboarded")
        layout.prop(data, "billboard_lock_x")
        layout.prop(data, "billboard_lock_y")
        layout.prop(data, "billboard_lock_z")
        col = layout.column(heading="Node")
        for prop in ("camera_anchored", "dont_inherit_translation", "dont_inherit_rotation", "dont_inherit_scaling"):
            if hasattr(data, prop):
                col.prop(data, prop)
