from typing import List

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
from ..process_warcraft_3_model import process_warcraft_3_model
from ... import mdl_constants
from ...classes.War3Model import War3Model


def parse_mdl(data: str, import_properties: MDXImportProperties):
    reader = Reader(data)
    model = War3Model("")
    model.file = import_properties.mdx_file_path
    data_chunks: List[str] = reader.chunks
    pivot_points: List[List[float]] = []

    for chunk in data_chunks:
        # print("new data chunk")
        label = chunk.split(" ", 1)[0]
        print(label)
        if label == mdl_constants.VERSION:
            model.version = parse_version(chunk)
        elif label == mdl_constants.MODEL:
            model.name = parse_model(chunk)
        elif label == mdl_constants.SEQUENCES:
            model.sequences.extend(parse_sequences(chunk))
        elif label == mdl_constants.TEXTURES:
            model.textures.extend(parse_textures(chunk))
        elif label == mdl_constants.MATERIALS:
            model.materials.extend(parse_materials(chunk))
        elif label == mdl_constants.GEOSET:
            geoset = parse_geosets(chunk)
            if geoset.name == "":
                geoset.name = str(len(model.geosets))
            model.geosets.append(geoset)
        elif label == mdl_constants.GEOSET_ANIM:
            model.geoset_anims.append(parse_geoset_animations(chunk))
        elif label == mdl_constants.BONE:
            model.bones.append(parse_bones(chunk))
        elif label == mdl_constants.HELPER:
            model.helpers.append(parse_helpers(chunk))
        elif label == mdl_constants.LIGHT:
            model.lights.append(parse_light(chunk))
        elif label == mdl_constants.ATTACHMENT:
            model.attachments.append(parse_attachments(chunk))
        elif label == mdl_constants.EVENT_OBJECT:
            model.event_objects.append(parse_events(chunk))
        elif label == mdl_constants.COLLISION_SHAPE:
            model.collision_shapes.append(parse_collision_shapes(chunk))
        elif label == mdl_constants.PARTICLE_EMITTER2:
            print("Particles not implemented yet")
        elif label == mdl_constants.PARTICLE_EMITTER:
            print("Particles not implemented yet")
        elif label == mdl_constants.TEXTURE_ANIMS:
            print("TextureAnims not implemented yet")
        elif label == mdl_constants.RIBBON_EMITTER:
            print("RibbonEmitter not implemented yet")
        elif label == mdl_constants.CAMERA:
            print("Camera not implemented yet")
        elif label == mdl_constants.UGG:
            print("X not implemented yet")
        elif label == mdl_constants.UGG:
            print("X not implemented yet")
        elif label == mdl_constants.PIVOT_POINTS:
            pivot_points.extend(parse_pivot_points(chunk))
            model.pivot_points.extend(pivot_points)

    process_warcraft_3_model(model)
    load_warcraft_3_model(model, import_properties)

