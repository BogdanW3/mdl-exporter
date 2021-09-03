from mathutils import Vector

from ..War3Model import War3Model
from ..War3Object import War3Object
from ..War3AnimationCurve import War3AnimationCurve
from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
from .is_animated_ugg import is_animated_ugg
from .create_bone import create_bone
from .get_visibility import get_visibility
from .register_global_sequence import register_global_sequence
from ..utils.transform_rot import transform_rot
from ..utils.transform_vec import transform_vec


def add_empties_animations(war3_model: War3Model, billboard_lock, billboarded, bpy_obj, parent, settings):
    visibility = get_visibility(war3_model.sequences, bpy_obj)
    anim_loc, anim_rot, anim_scale, is_animated = is_animated_ugg(war3_model, bpy_obj, settings)
    if bpy_obj.name.startswith("SND") or bpy_obj.name.startswith("UBR") or bpy_obj.name.startswith(
            "FTP") or bpy_obj.name.startswith("SPL"):
        eventobj = War3Object(bpy_obj.name)
        eventobj.pivot = settings.global_matrix @ Vector(bpy_obj.location)

        for datapath in ('["event_track"]', '["eventtrack"]', '["EventTrack"]'):
            eventobj.track = get_wc3_animation_curve(bpy_obj.animation_data, datapath, 1, war3_model.sequences)
            # get_curve(obj, ['["eventtrack"]', '["EventTrack"]', '["event_track"]'])

            if eventobj.track is not None:
                register_global_sequence(war3_model.global_seqs, eventobj.track)
                break

        war3_model.objects['eventobject'].add(eventobj)

    elif bpy_obj.name.endswith(" Ref"):
        att = War3Object(bpy_obj.name)
        att.pivot = settings.global_matrix @ Vector(bpy_obj.location)
        att.parent = parent
        att.visibility = visibility
        register_global_sequence(war3_model.global_seqs, visibility)
        att.billboarded = billboarded
        att.billboard_lock = billboard_lock
        war3_model.objects['attachment'].add(att)

    elif bpy_obj.name.startswith("Bone_"):
        bone = create_bone(anim_loc, anim_rot, anim_scale, bpy_obj, parent, settings)
        # bone = War3Object(obj.name)
        # if parent is not None:
        #     bone.parent = parent
        # bone.pivot = settings.global_matrix @ Vector(obj.location)
        # bone.anim_loc = anim_loc
        # bone.anim_scale = anim_scale
        # bone.anim_rot = anim_rot

        register_global_sequence(war3_model.global_seqs, bone.anim_scale)

        if bone.anim_loc is not None:
            register_global_sequence(war3_model.global_seqs, bone.anim_loc)
            transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                          bone.anim_loc.handles_left, bpy_obj.matrix_world.inverted())
            # if obj.parent is not None:
            #     bone.anim_loc.transform_vec(obj.parent.matrix_world.inverted())
            transform_vec(bone.anim_loc.keyframes, bone.anim_loc.interpolation, bone.anim_loc.handles_right,
                          bone.anim_loc.handles_left, settings.global_matrix)

        if bone.anim_rot is not None:
            register_global_sequence(war3_model.global_seqs, bone.anim_rot)
            transform_rot(bone.anim_rot.keyframes, bpy_obj.matrix_world.inverted())
            transform_rot(bone.anim_rot.keyframes, settings.global_matrix)

        bone.billboarded = billboarded
        bone.billboard_lock = billboard_lock
        war3_model.objects['bone'].add(bone)
