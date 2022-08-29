import typing

import bpy
from mathutils import Vector

from ..War3Emitter import War3Emitter
from ..War3ExportSettings import War3ExportSettings
from ..War3Model import War3Model
from ..War3ParticleEmitter import War3ParticleEmitter
from ..War3ParticleSystem import War3ParticleSystem
from .is_animated_ugg import is_animated_ugg
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence
from ..War3RibbonEmitter import War3RibbonEmitter
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec, transform_vec1


def add_particle_systems(war3_model: War3Model, billboard_lock, billboarded, mats: typing.Set[bpy.types.Material],
                         bpy_obj: bpy.types.Object, parent: typing.Optional[bpy.types.Object],
                         settings: War3ExportSettings):
    sequences = war3_model.sequences
    global_seqs = war3_model.global_seqs
    visibility = get_visibility(sequences, bpy_obj)
    anim_loc, anim_rot, anim_scale = is_animated_ugg(sequences, bpy_obj, settings)
    data = bpy_obj.particle_systems[0].settings

    if getattr(data, "mdl_particle_sys"):
        # particle_sys = War3ParticleSystem(bpy_obj.name, bpy_obj, war3_model)
        pivot = settings.global_matrix @ Vector(bpy_obj.location)
        if data.mdl_particle_sys.emiter_type == 'ParticleEmitter':
            particle_sys = War3ParticleEmitter(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent, pivot)
        elif settings.mdl_particle_sys.emiter_type == 'ParticleEmitter2':
            particle_sys = War3ParticleSystem(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent, pivot)
        elif settings.mdl_particle_sys.emiter_type == 'RibbonEmitter':
            particle_sys = War3RibbonEmitter(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent, pivot)
        else:
            particle_sys = War3Emitter(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent, pivot)

        # particle_sys = War3ParticleSystem(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent, pivot)
        particle_sys.set_from(bpy_obj, sequences, global_seqs)
        # particle_sys.pivot = pivot

        # particle_sys.dimensions = obj.matrix_world.to_quaternion() * Vector(obj.scale)
        particle_sys.dimensions = Vector(map(abs, settings.global_matrix @ bpy_obj.dimensions))

        # particle_sys.parent = parent
        particle_sys.visibility = visibility
        register_global_sequence(global_seqs, particle_sys.visibility)

        if any((anim_loc, anim_rot, anim_scale)):
            # particle = War3ParticleSystem(bpy_obj.name, anim_loc, anim_rot, anim_scale, parent, pivot)
            # particle.set_from(bpy_obj, sequences, global_seqs)
            register_global_sequence(global_seqs, particle_sys.anim_loc)
            register_global_sequence(global_seqs, particle_sys.anim_rot)
            register_global_sequence(global_seqs, particle_sys.anim_scale)

            if particle_sys.anim_loc is not None:
                # transform_vec(particle_sys.anim_loc.keyframes, particle_sys.anim_loc.interpolation,
                #               particle_sys.anim_loc.handles_right, particle_sys.anim_loc.handles_left,
                #               settings.global_matrix)
                transform_vec1(particle_sys.anim_loc, settings.global_matrix)

            if particle_sys.anim_rot is not None:
                transform_rot(particle_sys.anim_rot.keyframes, settings.global_matrix)

            particle_sys.billboarded = billboarded
            particle_sys.billboard_lock = billboard_lock
            # war3_model.objects['bone'].add(bone)
            # particle_sys.parent = bone.name

        if isinstance(particle_sys, War3ParticleEmitter):
            war3_model.particle_systems.append(particle_sys)

        elif isinstance(particle_sys, War3ParticleSystem):
            war3_model.particle_systems2.append(particle_sys)

        elif isinstance(particle_sys, War3RibbonEmitter):
            mat: bpy.types.Material = particle_sys.emitter.ribbon_material
            mats.add(mat)

            war3_model.particle_ribbon.append(particle_sys)

        # else:
        #     # Add the material to the list, in case it's unused
        #     mat: bpy.types.Material = particle_sys.emitter.ribbon_material
        #     mats.add(mat)
        #
        #     war3_model.particle_ribbon.append(particle_sys)
