# -- Object types -- #
# Bone
# Light
# Helper
# Attachment
# Particle Emitter
# Particle Emitter 2
# Ribbon Emitter
# Event Object
# Collision shape
# ------------------ #
import datetime
import getpass
from typing import List

import bpy
from mathutils import Matrix

from .save_attachment_points import save_attachment_points
from .save_bones import save_bones
from .save_cameras import save_cameras
from .save_collision_shape import save_collision_shape
from .save_event_objects import save_event_objects
from .save_geoset_animations import save_geoset_animations
from .save_geosets import save_geosets
from .save_global_sequences import save_global_sequences
from .save_helpers import save_helpers
from .save_lights import save_lights
from .save_materials import save_materials
from .save_model_emitters import save_model_emitters
from .save_model_header import save_model_header
from .save_particle_emitters import save_particle_emitters
from .save_pivot_points import save_pivot_points
from .save_ribbon_emitters import save_ribbon_emitters
from .save_sequences import save_sequences
from .save_texture_animations import save_texture_animations
from .save_textures import save_textures
from .write_mdx import write_mdx_file, bind_pose
from ..classes.War3ExportSettings import War3ExportSettings
from ..classes.War3Model import War3Model
from ..classes.model_utils.from_scene import from_scene
from ..utils import float2str
from ..action_compat import get_action_slot, restore_action


def save(operator, context: bpy.types.Context, settings: War3ExportSettings, filepath="", mdl_version=800,
         file_format='MDL'):

    print("Save, context: ", context)
    scene = context.scene

    current_frame = scene.frame_current
    obj_to_anim = {}  # save objects' active action
    for obj in scene.objects:
        if obj.animation_data is not None:
            obj_to_anim[obj] = (obj.animation_data.action, get_action_slot(obj))
    scene.frame_set(0)

    frame2ms: float = 1000 / context.scene.render.fps  # Frame to millisecond conversion
    model: War3Model = from_scene(context, settings)

    for obj, (anim, slot) in obj_to_anim.items():  # set objects' active actions
        restore_action(obj, anim, slot)
    scene.frame_set(current_frame)

    # Things the user should know about, the operator reports them as warnings
    warnings: List[str] = []
    hd_materials = [mat.name for mat in model.materials if mat.layers and mat.layers[0].hd]
    if hd_materials and mdl_version < 900:
        warnings.append("Version %d has no HD materials, wrote %s as SD" % (mdl_version, ", ".join(hd_materials)))

    if file_format == 'MDX':
        write_mdx_file(filepath, mdl_version, model, frame2ms, settings)
    else:
        write_model_file(filepath, mdl_version, model, frame2ms, settings)
    print('Done saving "%s"' % filepath)
    return warnings


def write_model_file(filepath: str, mdl_version: int, model: War3Model, frame2ms: float, settings: War3ExportSettings):
    with open(filepath, 'w') as output:
        fw = output.write

        date = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        fw("// Exported on %s by %s\n" % (date, getpass.getuser()))

        fw("Version {\n\tFormatVersion %d,\n}\n" % mdl_version)
        # HEADER
        save_model_header(fw, model)

        # SEQUENCES
        save_sequences(fw, model.sequences, model.global_extents_min, model.global_extents_max, frame2ms)

        # GLOBAL SEQUENCES
        save_global_sequences(fw, model.global_seqs)

        # TEXTURES
        save_textures(fw, model.textures)

        # MATERIALS
        save_materials(fw, model.materials, model.textures, model.tvertex_anims, model.global_seqs, mdl_version)

        # TEXTURE ANIMATIONS
        save_texture_animations(fw, model.tvertex_anims, model.global_seqs)

        # GEOSETS
        save_geosets(fw, model, settings, mdl_version)

        # GEOSET ANIMS
        save_geoset_animations(fw, model.geoset_anims, model.geosets, model.global_seqs)

        # BONES
        save_bones(fw, model)

        # LIGHTS
        save_lights(fw, model, mdl_version)

        # HELPERS
        save_helpers(fw, model)

        # ATTACHMENT POINTS
        save_attachment_points(fw, model.attachments, model.global_seqs)

        # PIVOT POINTS
        save_pivot_points(fw, model.objects_all)

        # MODEL EMITTERS
        save_model_emitters(fw, model.particle_systems, model.global_seqs)

        # PARTICLE EMITTERS
        save_particle_emitters(fw, model)

        # RIBBON EMITTERS
        save_ribbon_emitters(fw, model)

        # CAMERAS
        save_cameras(fw, model, settings)

        # EVENT OBJECTS
        save_event_objects(fw, model.event_objects, model.global_seqs)

        # COLLISION SHAPES
        save_collision_shape(fw, model.collision_shapes)

        has_hd = any(mat.layers and mat.layers[0].hd for mat in model.materials)
        if 900 <= mdl_version and has_hd:
            fw("BindPose {\n")
            fw("\tMatrices %s {\n" % (len(model.objects_all) + len(model.cameras)))
            for node in list(model.objects_all) + list(model.cameras):
                fw("\t\t{ %s },\n" % ", ".join(map(float2str, bind_pose(node))))
            fw("\t}\n")
            fw("}\n")


def mat_to_tuple(mat: Matrix):
    if mat is None:
        return 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0
    v_list: List[float] = []
    for row in mat:
        v_list.extend(list(row))
    return tuple(v_list)
