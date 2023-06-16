from typing import TextIO, List

from ..classes.War3Texture import War3Texture


def save_textures(fw: TextIO.write, textures: List[War3Texture]):
    if len(textures):
        fw("Textures %d {\n" % len(textures))
        for texture in textures:
            fw("\tBitmap {\n")

            if texture.texture_path.startswith("ReplaceableId"):
                fw("\t\tImage \"\",\n")
                fw("\t\tReplaceableId %s,\n" % texture.replaceable_id)
            else:
                fw("\t\tImage \"%s\",\n" % texture.texture_path)

            fw("\t\tWrapHeight,\n")
            fw("\t\tWrapWidth,\n")
            fw("\t}\n")
        fw("}\n")
