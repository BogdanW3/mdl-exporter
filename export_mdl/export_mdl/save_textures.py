from typing import TextIO

from ..classes.War3Model import War3Model


def save_textures(fw: TextIO.write, model: War3Model):
    if len(model.textures):
        fw("Textures %d {\n" % len(model.textures))
        for texture in model.textures:
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
