import bpy


class WAR3_OT_update_bone_settings(bpy.types.Operator):
    bl_idname = 'warcraft_3.update_bone_settings'
    bl_label = 'Warcraft 3 Update Bone Settings'
    bl_description = 'Warcraft 3 Update Bone Settings'
    bl_options = {'UNDO'}

    def execute(self, context):
        curr_object = context.object
        for bone in curr_object.data.bones:
            nodeType = bone.warcraft_3.nodeType
            boneGroup = curr_object.pose.bone_groups.get(nodeType.lower() + 's', None)
            if not boneGroup:
                if nodeType in {'BONE', 'ATTACHMENT', 'COLLISION_SHAPE', 'EVENT', 'HELPER'}:
                    bpy.ops.pose.group_add()
                    boneGroup = curr_object.pose.bone_groups.active
                    boneGroup.name = nodeType.lower() + 's'
                    if nodeType == 'BONE':
                        boneGroup.color_set = 'THEME04'
                    elif nodeType == 'ATTACHMENT':
                        boneGroup.color_set = 'THEME09'
                    elif nodeType == 'COLLISION_SHAPE':
                        boneGroup.color_set = 'THEME02'
                    elif nodeType == 'EVENT':
                        boneGroup.color_set = 'THEME03'
                    elif nodeType == 'HELPER':
                        boneGroup.color_set = 'THEME01'
                else:
                    boneGroup = None
            curr_object.pose.bones[bone.name].bone_group = boneGroup
        return {'FINISHED'}
