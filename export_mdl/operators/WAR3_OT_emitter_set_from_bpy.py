import math
from typing import Optional

import bpy


class WAR3_OT_emitter_set_from_bpy(bpy.types.Operator):
    bl_idname = 'war_3.emitter_set_from_bpy'
    bl_label = 'Warcraft 3 Set WC3 Particle Setting from Blender Particle Settings'
    bl_description = 'Warcraft 3 Set WC3 Particle Setting from Blender Particle Settings'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and len(context.active_object.particle_systems)

    def execute(self, context):
        p_sys: Optional[bpy.types.ParticleSettings] = context.active_object.particle_systems.active.settings
        p_settings = context.active_object.particle_systems.active.settings.mdl_particle_sys
        print(p_sys)
        if p_sys and p_settings:
            num = p_sys.count
            print(p_sys.child_type, (p_sys.child_type is 'NONE'), (p_sys.child_type == 'NONE'), (p_sys.child_type is None))
            if p_sys.child_type != 'NONE':
                num = num * p_sys.child_nbr
            time = p_sys.frame_end - p_sys.frame_start
            life_time = p_sys.lifetime
            p_settings.speed = p_sys.normal_factor * 10.0
            fps_translate = 1000.0 / bpy.context.scene.render.fps
            p_settings.emission_rate = num / time * fps_translate
            p_settings.life_span = life_time
            if p_sys.normal_factor != 0:
                var_factor = (p_sys.normal_factor - p_sys.factor_random) / p_sys.normal_factor
                p_settings.variation = min(max(-1.0, var_factor), 2.0)
                rand_factor = p_sys.factor_random / p_sys.normal_factor
                p_settings.latitude = min(max(0.0, rand_factor), 2.0) * 90
                if p_sys.effector_weights:
                    p_settings.gravity = p_sys.normal_factor * fps_translate * p_sys.effector_weights.gravity

        return {'FINISHED'}