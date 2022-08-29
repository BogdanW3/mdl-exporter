import bpy


def set_bone_node_type(self, context):
    bone = context.active_bone
    if bone:
        node_type = bone.warcraft_3.nodeType
        bpy_object = context.object
        bone_group = bpy_object.pose.bone_groups.get(node_type.lower() + 's', None)
        if not bone_group:
            if node_type in {'BONE', 'ATTACHMENT', 'COLLISION_SHAPE', 'EVENT', 'HELPER'}:
                bpy.ops.pose.group_add()
                bone_group = bpy_object.pose.bone_groups.active
                bone_group.name = node_type.lower() + 's'
                if node_type == 'BONE':
                    bone_group.color_set = 'THEME04'
                elif node_type == 'ATTACHMENT':
                    bone_group.color_set = 'THEME09'
                elif node_type == 'COLLISION_SHAPE':
                    bone_group.color_set = 'THEME02'
                elif node_type == 'EVENT':
                    bone_group.color_set = 'THEME03'
                elif node_type == 'HELPER':
                    bone_group.color_set = 'THEME01'
            else:
                bone_group = None
        bpy_object.pose.bones[bone.name].bone_group = bone_group


class War3NodeProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Bone
    nodeType: bpy.props.EnumProperty(
        items=[
            ('NONE', 'None', ''),
            ('BONE', 'Bone', ''),
            ('HELPER', 'Helper', ''),
            ('ATTACHMENT', 'Attachment', ''),
            ('EVENT', 'Event', ''),
            ('COLLISION_SHAPE', 'Collision Shape', '')
            ],
        name='Node Type',
        update=set_bone_node_type,
        default='NONE'
        )

