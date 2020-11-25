from mathutils import Vector

from ..War3Model import War3Model
from ..War3ParticleSystem import War3ParticleSystem
from .is_animated_ugg import is_animated_ugg
from .create_bone import create_bone
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec


def add_particle_systems(war3_model: War3Model, billboard_lock, billboarded, mats, obj, parent, settings):
    visibility = get_visibility(war3_model.sequences, obj)
    anim_loc, anim_rot, anim_scale, is_animated = is_animated_ugg(war3_model, obj, settings)
    data = obj.particle_systems[0].settings

    if getattr(data, "mdl_particle_sys"):
        particle_sys = War3ParticleSystem(obj.name, obj, war3_model)

        particle_sys.pivot = settings.global_matrix @ Vector(obj.location)

        # particle_sys.dimensions = obj.matrix_world.to_quaternion() * Vector(obj.scale)
        particle_sys.dimensions = Vector(map(abs, settings.global_matrix @ obj.dimensions))

        particle_sys.parent = parent
        particle_sys.visibility = visibility
        register_global_sequence(war3_model.global_seqs, particle_sys.visibility)

        if is_animated:
            bone = create_bone(anim_loc, anim_rot, anim_scale, obj, parent, settings)
            register_global_sequence(war3_model.global_seqs, bone.anim_loc)
            register_global_sequence(war3_model.global_seqs, bone.anim_rot)
            register_global_sequence(war3_model.global_seqs, bone.anim_scale)

            if bone.anim_loc is not None:
                transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation,
                              bone.anim_loc.handles_right, bone.anim_loc.handles_left,
                              settings.global_matrix)

            if bone.anim_rot is not None:
                transform_rot(bone.anim_rot.keyframes, settings.global_matrix)

            bone.billboarded = billboarded
            bone.billboard_lock = billboard_lock
            war3_model.objects['bone'].add(bone)
            particle_sys.parent = bone.name

        if particle_sys.emitter.emitter_type == 'ParticleEmitter':
            war3_model.objects['particle'].add(particle_sys)

        elif particle_sys.emitter.emitter_type == 'ParticleEmitter2':
            war3_model.objects['particle2'].add(particle_sys)

        else:
            # Add the material to the list, in case it's unused
            mat = particle_sys.emitter.ribbon_material
            mats.add(mat)

            war3_model.objects['ribbon'].add(particle_sys)
