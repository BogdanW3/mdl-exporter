from typing import TextIO, List

from io_scene_warcraft_3.classes.WarCraft3Texture import WarCraft3Texture
from ..classes.War3Model import War3Model


def save_textures(fw: TextIO.write, textures: List[WarCraft3Texture]):
    if len(textures):
        fw("Textures %d {\n" % len(textures))
        for texture in textures:
            fw("\tBitmap {\n")

            if texture.startswith("ReplaceableId"):
                fw("\t\tImage \"\",\n")
                fw("\t\t%s,\n" % texture)
            else:
                fw("\t\tImage \"%s\",\n" % texture)

            fw("\t\tWrapHeight,\n")
            fw("\t\tWrapWidth,\n")
            fw("\t}\n")
        fw("}\n")
