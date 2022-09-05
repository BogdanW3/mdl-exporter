import re
from typing import List

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

        for chunk in layer_chunks:
            layer = War3Layer()
            layer_info = extract_bracket_content(chunk).split(",")

            for info in layer_info:
                label = info.strip().split(" ")[0]

                if label == "FilterMode":
                    layer.filter_mode = get_between(info, "FilterMode ", ",")
                else:
                    if info.find("TextureID") > -1:
                        if info.find("static TextureID") > -1:
                            layer.texture_path = get_between(info, "static TextureID ", ",")
                        else:
                            # Flip-book texture on format time: textureID,
                            #   DontInterp,
                            # 	GlobalSeqId 0
                            # 	0: 0,
                            # 	...
                            texture_chunk = re.split(",\n*\\s*(?=TextureID)", chunk)[1]
                            layer.texture_anim = parse_geoset_transformation(texture_chunk)
                            layer.texture_path = get_between(info, "TextureID ", "{")

                    if info.find("Alpha") > -1:
                        if info.find("static Alpha") > -1:
                            layer.alpha_value = float(get_between(info, "static Alpha ", ","))
                        else:
                            alpha_chunk = re.split(",\n*\\s*(?=Alpha)", chunk)[1]
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

            layers.append(layer)

        material.layers = layers
        materials.append(material)
    return materials
