import bpy
from typing import Optional


def get_parent_name(bpy_obj: bpy.types.Object) -> Optional[str]:
    parent: bpy.types.Object = bpy_obj.parent

    # print("parent: ", parent)
    # print("parent_type: ", bpy_obj.parent_type)
    if parent is None:
        return None
    elif bpy_obj.parent_type == 'BONE':
        return bpy_obj.parent_bone if bpy_obj.parent_bone != "" else None
    elif parent.type == 'EMPTY':
        return parent.name
    elif parent.type == 'OBJECT':
        return parent.name
    elif parent.type == 'ARMATURE':
        return parent.name

    return get_parent_name(parent)

