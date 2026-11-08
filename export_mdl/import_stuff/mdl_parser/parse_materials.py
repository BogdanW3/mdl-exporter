import copy
import re
from typing import List

from ... import constants
from .parse_geoset_transformation import parse_geoset_transformation
from .mdl_reader import extract_bracket_content, chunkifier, get_between
from ...classes.War3Layer import War3Layer
from ...classes.War3Material import War3Material


def parse_materials(data: str) -> List[War3Material]:
    # print("parse_materials")
    materials_string = extract_bracket_content(data)
    material_chunks = chunkifier(materials_string)

    materials: List[War3Material] = []
    for material_chunk in material_chunks:
        material = War3Material("")
        material_info = extract_bracket_content(material_chunk)
        layer_chunks = chunkifier(material_info)
        layers = []

        # v900/v1000 name the shader once per material, v1100+ per layer
        material_shader = re.search(r'Shader\s+"([^"]*)"', material_info.split("Layer")[0])
        material_shader_id = constants.shader_id_from_name(material_shader.group(1)) if material_shader else 0

        for chunk in layer_chunks:
            layer = War3Layer()
            layer.shader = material_shader_id
            layer.hd = material_shader_id in constants.HD_SHADER_IDS
            layer_info = extract_bracket_content(chunk).split(",")
            slot_texture_ids: List[str] = []

            for info in layer_info:
                label = info.strip().split(" ")[0]

                if label == "FilterMode":
                    layer.filter_mode = get_between(info, "FilterMode ", ",")
                elif label == "Shader":
                    layer.shader = constants.shader_id_from_name(get_between(info, "Shader ", ",").strip('"'))
                    layer.hd = layer.shader in constants.HD_SHADER_IDS
                else:
                    if info.find("TextureID") > -1:
                        if info.find("static TextureID") > -1:
                            texture_id = get_between(info, "static TextureID ", ",")
                            if "<=" in texture_id:
                                # v1100+ HD: "static TextureID id <= slot", one line per PBR slot
                                texture_id = texture_id.split("<=")[0].strip()
                                slot_texture_ids.append(texture_id)
                            if len(slot_texture_ids) <= 1:
                                layer.texture_path = texture_id
                        else:
                            # Flip-book texture on format time: textureID,
                            #   DontInterp,
                            # 	GlobalSeqId 0
                            # 	0: 0,
                            # 	...
                            split = re.split(",\n*\\s*(?=TextureID)", chunk)
                            if 1 < len(split):
                                texture_chunk = split[1]
                                layer.texture_anim = parse_geoset_transformation(texture_chunk)
                                layer.texture_path = get_between(info, "TextureID ", "{")

                    if info.find("Alpha") > -1:
                        if info.find("static Alpha") > -1:
                            layer.alpha_value = float(get_between(info, "static Alpha ", ","))
                        else:
                            split = re.split(",\n*\\s*(?=Alpha)", chunk)
                            if 1 < len(split):
                                alpha_chunk = split[1]
                                layer.alpha_anim = parse_geoset_transformation(alpha_chunk)

                    # if info.find("FresnelColor") > -1:
                    #     if info.find("static FresnelColor") > -1:
                    #         layer.fresnel_color = float(get_between(info, "static FresnelColor ", ","))
                    #     else:
                    #         alpha_chunk = re.split(",\n*\\s*(?=FresnelOpacity)", chunk)[1]
                    #         layer.fresnel_color_anim = parse_geoset_transformation(alpha_chunk)
                    #
                    # if info.find("FresnelOpacity") > -1:
                    #     if info.find("static FresnelOpacity") > -1:
                    #         layer.fresnel_opacity = float(get_between(info, "static FresnelOpacity ", ","))
                    #     else:
                    #         alpha_chunk = re.split(",\n*\\s*(?=FresnelOpacity)", chunk)[1]
                    #         layer.fresnel_opacity_anim = parse_geoset_transformation(alpha_chunk)
                    #
                    # if info.find("FresnelTeamColor") > -1:
                    #     if info.find("static FresnelTeamColor") > -1:
                    #         layer.fresnel_team_color = float(get_between(info, "static FresnelTeamColor ", ","))
                    #     else:
                    #         alpha_chunk = re.split(",\n*\\s*(?=FresnelTeamColor)", chunk)[1]
                    #         layer.fresnel_team_color_anim = parse_geoset_transformation(alpha_chunk)

            if 1 < len(slot_texture_ids):
                # Split into one layer per texture, the layout the material importer expects for HD
                for texture_id in slot_texture_ids:
                    slot_layer = copy.copy(layer)
                    slot_layer.texture_path = texture_id
                    layers.append(slot_layer)
            else:
                layers.append(layer)

        material.layers = layers
        materials.append(material)
    return materials
