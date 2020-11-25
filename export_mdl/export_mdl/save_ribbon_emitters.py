from .write_mdl import write_mdl
from ..utils import f2s, rnd


def save_ribbon_emitters(fw, model):
    for psys in model.objects['ribbon']:
        emitter = psys.emitter
        fw("RibbonEmitter \"%s\" {\n" % psys.name)
        if len(model.object_indices) > 1:
            fw("\tObjectId %d,\n" % model.object_indices[psys.name])
        if psys.parent is not None:
            fw("\tParent %d,\n" % model.object_indices[psys.parent])

        fw("\tstatic HeightAbove %s,\n" % f2s(rnd(psys.dimensions[0] / 2)))
        fw("\tstatic HeightBelow %s,\n" % f2s(rnd(psys.dimensions[0] / 2)))

        if psys.alpha_anim is not None:
            write_mdl(psys.alpha_anim.keyframes, psys.alpha_anim.type,
                      psys.alpha_anim.interpolation, psys.alpha_anim.global_sequence,
                      psys.alpha_anim.handles_left, psys.alpha_anim.handles_right,
                      "Alpha", fw, model.global_seqs, "\t")
        else:
            fw("\tstatic Alpha %s,\n" % emitter.alpha)

        if psys.ribbon_color_anim is not None:
            write_mdl(psys.ribbon_color_anim.keyframes, psys.ribbon_color_anim.type,
                      psys.ribbon_color_anim.interpolation, psys.ribbon_color_anim.global_sequence,
                      psys.ribbon_color_anim.handles_left, psys.ribbon_color_anim.handles_right,
                      "Color", fw, model.global_seqs, "\t")
            # write_anim_vec(psys.ribbon_color_anim, 'Color', 'ribbon_color', fw, global_seqs, Matrix(), Matrix(), "\t", (2, 1, 0))
        else:
            fw("\tstatic Color {%s, %s, %s},\n" % tuple(map(f2s, reversed(emitter.ribbon_color))))

        fw("\tstatic TextureSlot %d,\n" % model.textures.index(emitter.texture_path))

        visibility = psys.visibility
        if visibility is not None:
            write_mdl(visibility.keyframes, visibility.type,
                      visibility.interpolation, visibility.global_sequence,
                      visibility.handles_left, visibility.handles_right,
                      "Visibility", fw, model.global_seqs, "\t")
            # write_anim(visibility, "Visibility", fw, global_seqs, "\t", True)

        fw("\tEmissionRate %d,\n" % emitter.emission_rate)
        fw("\tLifeSpan %s,\n" % f2s(rnd(emitter.life_span)))
        fw("\tGravity %s,\n" % f2s(rnd(emitter.gravity)))
        fw("\tRows %d,\n" % emitter.rows)
        fw("\tColumns %d,\n" % emitter.cols)

        for material in model.materials:
            if material.name == emitter.ribbon_material.name:
                fw("\tMaterialID %d,\n" % model.materials.index(material))
                break
        fw("}\n")
