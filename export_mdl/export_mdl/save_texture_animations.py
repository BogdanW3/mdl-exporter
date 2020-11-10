def save_texture_animations(fw, model):
    if len(model.tvertex_anims):
        fw("TextureAnims %d {\n" % len(model.tvertex_anims))
        for uv_anim in model.tvertex_anims:
            fw("\tTVertexAnim {\n")
            if uv_anim.translation is not None:
                uv_anim.translation.write_mdl("Translation", fw, model.global_seqs, "\t\t")

            if uv_anim.rotation is not None:
                uv_anim.rotation.write_mdl("Rotation", fw, model.global_seqs, "\t\t")

            if uv_anim.scale is not None:
                uv_anim.scaling.write_mdl("Scaling", fw, model.global_seqs, "\t\t")

            fw("\t}\n")
        fw("}\n")
    material_names = [mat.name for mat in model.materials]
    return material_names
