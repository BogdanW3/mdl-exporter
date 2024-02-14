from typing import List, Dict

import bpy

from ..classes.War3Model import War3Model
from ..import_stuff import War3BpyMaterial
from ..import_stuff.MDXImportProperties import MDXImportProperties
from ..import_stuff.create_armature_actions import create_armature_actions
from ..import_stuff.create_armature_object import create_armature_object
from ..import_stuff.create_material import create_material
from ..import_stuff.create_mesh_objects import create_mesh_objects
from ..import_stuff.create_object_actions import create_geoset_actions
from ..import_stuff.create_other_objects import create_other_objects


def load_warcraft_3_model(model: War3Model, import_properties: MDXImportProperties):
    bpy_materials: Dict[str, War3BpyMaterial] = create_material(model, import_properties.team_color)
    armature_object: bpy.types.Object = create_armature_object(model, import_properties.bone_size)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.active_object.select_set(False)
    bpy_mesh_objects: List[bpy.types.Object] = create_mesh_objects(model, armature_object, bpy_materials)

    create_armature_actions(armature_object, model, import_properties.frame_time)
    create_other_objects(model, armature_object, import_properties.bone_size, import_properties.frame_time)
    create_geoset_actions(model, bpy_mesh_objects, import_properties.frame_time)

