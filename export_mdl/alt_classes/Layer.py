from typing import Optional, Dict

from export_mdl.alt_classes.ComponentTransform import ComponentTransform
from export_mdl.alt_classes.Sequence import Sequence
from export_mdl.alt_classes.TextureAnimaton import TextureAnimation


class Layer:
    def __init__(self):
        self.texture: str = "Textures\\white.blp"
        self.filter_mode: str = "None"
        self.unshaded: bool = False
        self.two_sided: bool = False
        self.unfogged: bool = False
        self.transforms: Dict[Sequence, ComponentTransform] = {}
        self.texture_anim: Optional[TextureAnimation] = None
        self.alpha_value: float = 1.0
        self.no_depth_test: bool = False
        self.no_depth_set: bool = False

