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

import bpy

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
from ..classes.War3ExportSettings import War3ExportSettings
from ..classes.War3Model import War3Model
from ..classes.bpy_helpers.bpy_scene_helper import BpySceneObjects
from ..classes.model_utils.from_scene2 import from_scene
from ..classes.model_utils.make_mesh2 import make_geosets


def save(operator, context: bpy.types.Context, settings: War3ExportSettings, filepath="", mdl_version=800):

    print("context: ", context)
    scene = context.scene

    current_frame = scene.frame_current
    scene.frame_set(0)

    frame2ms: float = 1000 / context.scene.render.fps  # Frame to millisecond conversion
    model = from_scene(context, settings)


    scene.frame_set(current_frame)

    write_model_file(filepath, mdl_version, model, settings)


def write_model_file(filepath, mdl_version, model, settings):
    with open(filepath, 'w') as output:
        fw = output.write

        date = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        fw("// Exported on %s by %s\n" % (date, getpass.getuser()))

        if settings.use_skinweights:
            fw("Version {\n\tFormatVersion %d,\n}\n" % 900)
        else:
            fw("Version {\n\tFormatVersion %d,\n}\n" % mdl_version)
        # HEADER
        save_model_header(fw, model)

        # SEQUENCES
        save_sequences(fw, model.sequences, model.global_extents_min, model.global_extents_max)

        # GLOBAL SEQUENCES
        save_global_sequences(fw, model.global_seqs)

        # TEXTURES
        save_textures(fw, model.textures)

        # MATERIALS
        save_materials(fw, model.materials, model.textures, model.tvertex_anims, model.global_seqs)

        # TEXTURE ANIMATIONS
        material_names = save_texture_animations(fw, model.tvertex_anims, model.materials, model.global_seqs)

        # GEOSETS
        save_geosets(fw, material_names, model, settings)

        # GEOSET ANIMS
        save_geoset_animations(fw, model.geoset_anims, model.geosets, model.global_seqs)

        # BONES
        save_bones(fw, model)

        # LIGHTS
        save_lights(fw, model)

        # HELPERS
        save_helpers(fw, model)

        # ATTACHMENT POINTS
        # save_attachment_points(fw, model)
        save_attachment_points(fw, model.attachments, model.global_seqs, model.object_indices)

        # PIVOT POINTS
        save_pivot_points(fw, model.objects_all)

        # MODEL EMITTERS
        save_model_emitters(fw, model.particle_systems, model.object_indices, model.global_seqs)

        # PARTICLE EMITTERS
        save_particle_emitters(fw, model)

        # RIBBON EMITTERS
        save_ribbon_emitters(fw, model)

        # CAMERAS
        save_cameras(fw, model, settings)

        # EVENT OBJECTS
        save_event_objects(fw, model.event_objects, model.object_indices, model.global_seqs)

        # COLLISION SHAPES
        save_collision_shape(fw, model)
