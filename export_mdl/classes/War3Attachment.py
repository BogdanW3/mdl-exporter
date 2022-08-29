from typing import Optional, List

from .War3AnimationCurve import War3AnimationCurve
from .War3Node import War3Node


class War3Attachment(War3Node):
    def __init__(self, name: str,
                 anim_loc: Optional[War3AnimationCurve],
                 anim_rot: Optional[War3AnimationCurve],
                 anim_scale: Optional[War3AnimationCurve],
                 parent: Optional[str], pivot: Optional[List[float]]):
        super().__init__(name, anim_loc, anim_rot, anim_scale, parent, pivot)
