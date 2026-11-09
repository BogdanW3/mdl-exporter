from typing import List, Dict

import bpy

from ..classes.War3Model import War3Model
from ..frame_rate import model_times, fit_scene_to, change_frame_rate, scene_fps, timing_error
from ..import_stuff import War3BpyMaterial
from ..import_stuff.MDXImportProperties import MDXImportProperties
from ..import_stuff.create_armature_actions import create_armature_actions
from ..import_stuff.create_armature_object import create_armature_object
from ..import_stuff.create_material import create_material, fill_material_layers
from ..import_stuff.create_mesh_objects import create_mesh_objects
from ..import_stuff.create_object_actions import create_geoset_actions
from ..import_stuff.create_node_objects import create_node_objects, armature_node_names


def set_frame_rate(model: War3Model, import_properties: MDXImportProperties):
    """Pick the scene rate the keys go on, before any are made."""
    scene = bpy.context.scene
    old = scene_fps(scene)
    times = model_times(model)
    if import_properties.frame_rate == 'FIT':
        rate = fit_scene_to(scene, times)
        if rate is not None:
            import_properties.messages.append(
                "Scene frame rate changed from %g to %d fps, so every key lands on a whole frame" % (old, rate))
    elif import_properties.frame_rate == 'CUSTOM':
        rate = int(round(import_properties.fps))
        if abs(old - rate) > 1e-9:
            change_frame_rate(scene, rate)
            import_properties.messages.append("Scene frame rate changed from %g to %d fps" % (old, rate))
    fps = scene_fps(scene)
    import_properties.fps = fps
    import_properties.frame_time = 1000 / fps
    error = timing_error(times, fps)
    if error:
        import_properties.messages.append(
            "At %g fps some keys moved by up to %d ms to land on whole frames" % (fps, error))


def load_warcraft_3_model(model: War3Model, import_properties: MDXImportProperties):
    set_frame_rate(model, import_properties)
    bpy_materials: Dict[str, War3BpyMaterial] = create_material(model, import_properties.team_color)
    # Only bones, helpers and nodes a skin needs become armature bones; the other nodes become objects
    bone_node_names = armature_node_names(model)
    model.armature_nodes = [node for node in model.id_to_object.values() if node.name in bone_node_names]
    armature_object: bpy.types.Object = create_armature_object(model, import_properties.bone_size)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.active_object.select_set(False)
    bpy_mesh_objects: List[bpy.types.Object] = create_mesh_objects(model, armature_object, bpy_materials)

    create_armature_actions(armature_object, model, import_properties.frame_time)
    create_node_objects(model, armature_object, import_properties.bone_size, import_properties.frame_time)
    create_geoset_actions(model, bpy_mesh_objects, import_properties.frame_time)
    fill_material_layers(model, bpy_materials, import_properties.frame_time)

