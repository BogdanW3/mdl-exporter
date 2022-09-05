from typing import List

from .mdl_reader import extract_bracket_content, chunkifier
from ...classes.War3Texture import War3Texture


def parse_textures(data: str) -> List[War3Texture]:
    textures_string = extract_bracket_content(data)
    texture_chunks = chunkifier(textures_string)

    textures: List[War3Texture] = []
    for texture_chunk in texture_chunks:
        label = texture_chunk.strip().split(" ")[0]
        if label == "Bitmap":
            texture = War3Texture()
            texture_info = extract_bracket_content(texture_chunk)
            label = texture_info.strip().split(" ")[0]

            if label == "Image":
                texture.texture_path = texture_info.strip().split("\"")[1]

            if label == "ReplaceableId":
                texture.replaceable_id = int(texture_info.strip().replace(",", "").split(" ")[1])

            if texture_info.find("WrapWidth") > -1:
                texture.wrap_width = True

            if texture_info.find("WrapHeight") > -1:
                texture.wrap_height = True

            textures.append(texture)
    return textures
