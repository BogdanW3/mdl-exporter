from typing import Optional, Tuple, List

import bpy
from mathutils import Vector, Matrix

from export_mdl.classes.model_utils.get_parent_name import get_parent_name
from export_mdl.properties import War3LightSettings


class BpyLight:
    def __init__(self, bpy_obj: bpy.types.Object, global_matrix: Matrix):
        self.bpy_obj: bpy.types.Object = bpy_obj
        self.matrix_world: Matrix = bpy_obj.matrix_world
        self.location: Vector = Vector(bpy_obj.location)
        self.pivot: Vector = global_matrix @ Vector(bpy_obj.location)
        self.name: str = bpy_obj.name

        self.bpy_light: bpy.types.Light = bpy_obj.data
        if hasattr(self.bpy_light, "mdl_light"):
            self.light_data: Optional[War3LightSettings] = self.bpy_light.mdl_light
        else:
            self.light_data = None

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
