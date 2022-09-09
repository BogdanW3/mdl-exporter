from typing import List, Dict

import bpy

from export_mdl.classes.War3Model import War3Model
from export_mdl.import_stuff import War3BpyMaterial
from export_mdl.import_stuff.MDXImportProperties import MDXImportProperties
from export_mdl.import_stuff.create_armature_actions import create_armature_actions
from export_mdl.import_stuff.create_armature_object import create_armature_object
from export_mdl.import_stuff.create_material import create_material
from export_mdl.import_stuff.create_mesh_objects import create_mesh_objects
from export_mdl.import_stuff.create_object_actions import create_object_actions


def load_warcraft_3_model(model: War3Model, import_properties: MDXImportProperties):
    # bpy_materials: Dict[str, bpy.types.Material] = create_material(model, import_properties.team_color)
    bpy_materials: Dict[str, War3BpyMaterial] = create_material(model, import_properties.team_color)
    armature_object: bpy.types.Object = create_armature_object(model, import_properties.bone_size)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.active_object.select_set(False)
    bpy_mesh_objects: List[bpy.types.Object] = create_mesh_objects(model, armature_object, bpy_materials)

    create_armature_actions(armature_object, model, import_properties.frame_time)
    create_object_actions(model, bpy_mesh_objects, import_properties.frame_time)

