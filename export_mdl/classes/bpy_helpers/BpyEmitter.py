from typing import Optional, Tuple, List

import bpy
from mathutils import Matrix, Vector

from export_mdl.classes.model_utils.get_parent import get_parent_name
from export_mdl.properties import War3ParticleSystemProperties


class BpyEmitter:
    def __init__(self, bpy_obj: bpy.types.Object, global_matrix: Matrix, particle_settings: War3ParticleSystemProperties):
        self.bpy_obj = bpy_obj
        self.location: Vector = Vector(bpy_obj.location)
        self.pivot = global_matrix @ Vector(bpy_obj.location)
        self.name = bpy_obj.name

        self.particle_system: bpy.types.ParticleSystem = bpy_obj.particle_systems[0]
        self.particle_settings: War3ParticleSystemProperties = particle_settings
        # self.material: bpy.types.Material = self.particle_settings.ribbon_material
        # self.ribbon_color: List[float] = self.particle_settings.ribbon_color

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

