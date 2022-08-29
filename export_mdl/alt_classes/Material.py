from typing import List

from export_mdl.alt_classes.Layer import Layer


class Material:
    def __init__(self):
        self.name: str = ""
        self.shader: str = ""
        self.layers: List[Layer] = []
        self.use_const_color: bool = False
        self.priority_plane: int = 0
