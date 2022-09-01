from typing import Optional, List

from mathutils import Matrix

from .War3AnimationCurve import War3AnimationCurve
from .War3Node import War3Node


class War3Attachment(War3Node):
    def __init__(self, name: str,
                 anim_loc: Optional[War3AnimationCurve] = None,
                 anim_rot: Optional[War3AnimationCurve] = None,
                 anim_scale: Optional[War3AnimationCurve] = None,
                 parent: Optional[str] = None,
                 pivot: List[float] = [0, 0, 0],
                 bindpose: Optional[Matrix] = None):
        super().__init__(name, anim_loc, anim_rot, anim_scale, parent, pivot, bindpose)
