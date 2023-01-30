from typing import Dict, List

from .parse_light import parse_light
from .mdl_reader import Reader
from .parse_attachments import parse_attachments
from .parse_bones import parse_bones
from .parse_collision_shapes import parse_collision_shapes
from .parse_events import parse_events
from .parse_geoset_animations import parse_geoset_animations
from .parse_geosets import parse_geosets
from .parse_helpers import parse_helpers
from .parse_materials import parse_materials
from .parse_model import parse_model
from .parse_pivot_points import parse_pivot_points
from .parse_sequences import parse_sequences
from .parse_textures import parse_textures
from .parse_version import parse_version
from ..MDXImportProperties import MDXImportProperties
from ..load_warcraft_3_model import load_warcraft_3_model
from ...classes.War3Model import War3Model
from ...classes.War3Node import War3Node
from ...classes.War3Texture import War3Texture


def parse_mdl(data: str, import_properties: MDXImportProperties):
    reader = Reader(data)
    model = War3Model("")
    model.file = import_properties.mdx_file_path
    data_chunks: List[str] = reader.chunks
    id_to_node: Dict[str, War3Node] = {}
    pivot_points: List[List[float]] = []

    for chunk in data_chunks:
        # print("new data chunk")
        label = chunk.split(" ", 1)[0]
        print(label)
        if label == "Version":
            model.version = parse_version(chunk)
        elif label == "Geoset":
            geoset = parse_geosets(chunk)
            if geoset.name == "":
                geoset.name = str(len(model.geosets))
            model.geosets.append(geoset)
        elif label == "GeosetAnim":
            model.geoset_anims.append(parse_geoset_animations(chunk))
        elif label == "Textures":
            model.textures.extend(parse_textures(chunk))
        elif label == "Materials":
            model.materials.extend(parse_materials(chunk))
        elif label == "Model":
            model.name = parse_model(chunk)
        elif label == "Bone":
            model.bones.append(parse_bones(chunk, id_to_node))
        elif label == "PivotPoints":
            pivot_points.extend(parse_pivot_points(chunk))
        elif label == "Helper":
            model.helpers.append(parse_helpers(chunk, id_to_node))
        elif label == "Light":
            model.lights.append(parse_light(chunk, id_to_node))
        elif label == "Attachment":
            model.attachments.append(parse_attachments(chunk, id_to_node))
        elif label == "EventObject":
            model.event_objects.append(parse_events(chunk, id_to_node))
        elif label == "CollisionShape":
            model.collision_shapes.append(parse_collision_shapes(chunk, id_to_node))
        elif label == "Sequences":
            model.sequences.extend(parse_sequences(chunk))
        elif label == "ParticleEmitter2":
            print("Particles not implemented yet")
        elif label == "TextureAnims":
            print("TextureAnims not implemented yet")
        elif label == "RibbonEmitter":
            print("RibbonEmitter not implemented yet")
        elif label == "Camera":
            print("Camera not implemented yet")
        elif label == "Ugg":
            print("X not implemented yet")
        elif label == "Ugg":
            print("X not implemented yet")

    for i, node in enumerate(id_to_node.values()):
        node.pivot = pivot_points[i]
        # print("node #", i, ":", node)
        if node.parent:
            # print("parent: ", node.parent)
            node.parent = id_to_node[node.parent].name

    for node_id, node in id_to_node.items():
        model.object_indices[node.name] = int(node_id)

    for geoset in model.geosets:
        if geoset.name is None:
            geoset.name = model.name
        elif geoset.name.isnumeric():
            geoset.name = geoset.name + " " + model.name
        # geoset.mat_name = model.materials[int(geoset.mat_name)].name
        for mg in geoset.matrices:
            b_names = []
            for bone in mg:
                b_names.append(id_to_node[bone].name)
            mg.clear()
            mg.extend(b_names)
        for vert in geoset.vertices:
            b_names = []
            for bone in vert.bone_list:
                if bone in id_to_node:
                    b_names.append(id_to_node[bone].name)
            if b_names:
                vert.bone_list.clear()
                vert.bone_list.extend(b_names)

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

    load_warcraft_3_model(model, import_properties)

