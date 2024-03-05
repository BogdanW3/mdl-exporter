from ..classes.War3Model import War3Model
from ..classes.War3Texture import War3Texture


def process_warcraft_3_model(model: War3Model):
    model.process_nodes()

    for geoset in model.geosets:
        if geoset.name is None:
            geoset.name = model.name
        elif geoset.name.isnumeric():
            geoset.name = geoset.name + " " + model.name

        for mg in geoset.matrices:
            b_names = []
            for bone in mg:
                # b_names.append(id_to_node[bone].name)
                b_names.append(model.id_to_object[int(bone)].name)
            mg.clear()
            mg.extend(b_names)

        # for vert in geoset.vertices:
        #     b_names = []
        #     b_ids = []
        #     for bone in vert.bone_list:
        #         if int(bone) in model.id_to_object:
        #             b_names.append(model.id_to_object[int(bone)].name)
        #             b_ids.append(int(bone))
        #     if b_names:
        #         vert.bone_list.clear()
        #         vert.bone_list.extend(b_names)
        #         vert.bone_id_list.clear()
        #         vert.bone_id_list.extend(b_ids)
        #         vert.bone_name_list.clear()
        #         vert.bone_name_list.extend(b_names)

    for geoset_anim in model.geoset_anims:
        geoset_anim.geoset = model.geosets[geoset_anim.geoset_id]
        if geoset_anim.geoset and geoset_anim.geoset.name:
            geoset_anim.geoset_name = geoset_anim.geoset.name
        else:
            geoset_anim.geoset_name = "%s" % geoset_anim.geoset_id + " " + model.name

    # print("model.materials:", model.materials)
    if len(model.textures) == 0:
        model.textures.append(War3Texture())
    for material in model.materials:
        for layer in material.layers:
            if int(layer.texture_path) < len(model.textures):
                layer.texture = model.textures[int(layer.texture_path)]
            else:
                layer.texture = model.textures[0]

    model.objects_all.extend(model.bones)
    model.objects_all.extend(model.helpers)

