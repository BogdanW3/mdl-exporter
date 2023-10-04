from typing import Optional, Tuple, List

import bpy
from mathutils import Matrix, Vector

from export_mdl.classes.model_utils.get_parent_name import get_parent_name


class BpyEmptyNode:
    def __init__(self, bpy_obj: bpy.types.Object, global_matrix: Matrix):
        self.bpy_obj: bpy.types.Object = bpy_obj
        self.matrix_world: Matrix = bpy_obj.matrix_world
        self.display_type = bpy_obj.empty_display_type
        self.location: Vector = Vector(bpy_obj.location)
        self.pivot = global_matrix @ Vector(bpy_obj.location)
        self.name: str = bpy_obj.name

        if hasattr(bpy_obj, "mdl_billboard"):
            bb = bpy_obj.mdl_billboard
            self.billboarded: bool = bb.billboarded
            self.billboard_lock: Tuple[bool, bool, bool] = (
                bb.billboard_lock_z,
                bb.billboard_lock_y,
                bb.billboard_lock_x)
        else:
            self.billboarded: bool = False
            self.billboard_lock: Tuple[bool, bool, bool] = (False, False, False)
        self.parent_name: Optional[str] = get_parent_name(bpy_obj)
        self.animation_data: bpy.types.AnimData = bpy_obj.animation_data
        self.should_be_bone = False
        if bpy_obj.children:
            for ch in bpy_obj.children:
                if ch.type == 'MESH' or ch.type == 'CURVE':
                    self.should_be_bone = True
                    break
