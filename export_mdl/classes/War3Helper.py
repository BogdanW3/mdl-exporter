from typing import Optional, List

from .War3AnimationCurve import War3AnimationCurve
from .War3Node import War3Node


class War3Helper(War3Node):
    def __init__(self, name: str,
                 anim_loc: Optional[War3AnimationCurve],
                 anim_rot: Optional[War3AnimationCurve],
                 anim_scale: Optional[War3AnimationCurve],
                 parent: Optional[str], pivot: Optional[List[float]]):
        super().__init__(name, anim_loc, anim_rot, anim_scale, parent, pivot)

    def __unit__(self, obj, model):
        War3Node.__init__(self, obj.name)
        model.objects['helper'].add(self)
