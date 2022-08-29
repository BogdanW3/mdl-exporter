from typing import Optional

from export_mdl.classes.War3AnimationCurve import War3AnimationCurve
from export_mdl.classes.War3TextureAnim import War3TextureAnim


class War3Layer:
    def __init__(self):
        self.texture: str = "Textures\\white.blp"
        self.filter_mode: str = "None"
        self.unshaded: bool = False
        self.two_sided: bool = False
        self.unfogged: bool = False
        self.texture_anim: Optional[War3TextureAnim] = None
        self.alpha_anim: Optional[War3AnimationCurve] = None
        self.alpha_value: float = 1.0
        self.no_depth_test: bool = False
        self.no_depth_set: bool = False

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
