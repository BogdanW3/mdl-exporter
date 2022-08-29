from typing import TextIO

from .write_animation_chunk import write_animation_chunk
from ..classes.War3Model import War3Model
from ..utils import float2str, rnd


def save_ribbon_emitters(fw: TextIO.write, model: War3Model):
    particle_ribbon = model.particle_ribbon
    object_indices = model.object_indices
    global_seqs = model.global_seqs
    materials = model.materials
    textures = model.textures
    for psys in particle_ribbon:
        psys.write_ribbon(fw, object_indices, global_seqs, textures, materials)
        # emitter = psys.emitter
        # fw("RibbonEmitter \"%s\" {\n" % psys.name)
        # if len(object_indices) > 1:
        #     fw("\tObjectId %d,\n" % object_indices[psys.name])
        # if psys.parent is not None:
        #     fw("\tParent %d,\n" % object_indices[psys.parent])
        #
        # fw("\tstatic HeightAbove %s,\n" % float2str(rnd(psys.dimensions[0] / 2)))
        # fw("\tstatic HeightBelow %s,\n" % float2str(rnd(psys.dimensions[0] / 2)))
        #
        # if psys.alpha_anim is not None:
        #     write_animation_chunk(psys.alpha_anim.keyframes, psys.alpha_anim.type,
        #                           psys.alpha_anim.interpolation, psys.alpha_anim.global_sequence,
        #                           psys.alpha_anim.handles_left, psys.alpha_anim.handles_right,
        #                           "Alpha", fw, global_seqs, "\t")
        # else:
        #     fw("\tstatic Alpha %s,\n" % emitter.alpha)
        #
        # if psys.ribbon_color_anim is not None:
        #     write_animation_chunk(psys.ribbon_color_anim.keyframes, psys.ribbon_color_anim.type,
        #                           psys.ribbon_color_anim.interpolation, psys.ribbon_color_anim.global_sequence,
        #                           psys.ribbon_color_anim.handles_left, psys.ribbon_color_anim.handles_right,
        #                           "Color", fw, global_seqs, "\t")
        #     # write_anim_vec(psys.ribbon_color_anim, 'Color', 'ribbon_color', fw, global_seqs, Matrix(), Matrix(), "\t", (2, 1, 0))
        # else:
        #     fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(float2str, reversed(emitter.ribbon_color))))
        #
        # fw("\tstatic TextureSlot %d,\n" % textures.index(emitter.texture_path))
        #
        # visibility = psys.visibility
        # if visibility is not None:
        #     write_animation_chunk(visibility.keyframes, visibility.type,
        #                           visibility.interpolation, visibility.global_sequence,
        #                           visibility.handles_left, visibility.handles_right,
        #                           "Visibility", fw, global_seqs, "\t")
        #     # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)
        #
        # fw("\tEmissionRate %d,\n" % emitter.emission_rate)
        # fw("\tLifeSpan %s,\n" % float2str(rnd(emitter.life_span)))
        # fw("\tGravity %s,\n" % float2str(rnd(emitter.gravity)))
        # fw("\tRows %d,\n" % emitter.rows)
        # fw("\tColumns %d,\n" % emitter.cols)
        #
        # for material in materials:
        #     if material.name == emitter.ribbon_material.name:
        #         fw("\tMaterialID %d,\n" % materials.index(material))
        #         break
        # fw("}\n")
