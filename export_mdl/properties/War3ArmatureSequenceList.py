import bpy


class War3ArmatureSequenceList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    length: bpy.props.IntProperty(min=0)
